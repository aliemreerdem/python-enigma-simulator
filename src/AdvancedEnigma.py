import string

# Extended alphabet: A-Z plus digits 0-9 (total 36 characters)
alphabet = string.ascii_uppercase + "0123456789"

class Rotor:
    def __init__(self, wiring, position=0):
        """
        Represents a rotor with a given permutation (wiring) of the extended alphabet.
        
        wiring: A permutation string of length 36 (A-Z0-9).
        position: The initial offset (0 <= position < 36).
        """
        self.alphabet = alphabet
        self.wiring = wiring
        self.position = position % len(self.alphabet)

    def encode_forward(self, c):
        """
        Encodes a character 'c' going forward (right-to-left direction in a classical Enigma sense).
        The character index is shifted by the rotor's current position before substitution.
        """
        idx = (self.alphabet.index(c) + self.position) % len(self.alphabet)
        return self.wiring[idx]

    def encode_backward(self, c):
        """
        Encodes a character 'c' going backward (left-to-right direction).
        This reverses the forward encoding step by finding the index of 'c' in the wiring and 
        adjusting by the rotor's position.
        """
        idx = self.wiring.index(c)
        return self.alphabet[(idx - self.position) % len(self.alphabet)]

    def step(self, steps=1):
        """
        Advances the rotor by 'steps' positions.
        This increases unpredictability as rotors do not just step by one, but by a varying amount.
        """
        self.position = (self.position + steps) % len(self.alphabet)

class ReflectorSet:
    def __init__(self, reflectors):
        """
        A set of reflectors. Instead of just one reflector, we have multiple reflector wirings.
        We will pick which reflector to use based on the key-derived offset.
        
        reflectors: A list of reflector wiring strings, each length 36.
        """
        self.alphabet = alphabet
        self.reflectors = reflectors

    def reflect(self, c, index=0):
        """
        Reflects character 'c' using the reflector at position 'index'.
        This introduces a polyalphabetic-like approach to reflection.
        """
        wiring = self.reflectors[index % len(self.reflectors)]
        idx = self.alphabet.index(c)
        return wiring[idx]

class Plugboard:
    def __init__(self, connections=None):
        """
        The plugboard allows swapping pairs of characters before and after the rotor encryption.
        
        connections: A dictionary like {'A':'D','D':'A','P':'X','X':'P',...}
        If None, no substitutions are made.
        """
        self.alphabet = alphabet
        self.mapping = {ch: ch for ch in self.alphabet}
        if connections:
            for a, b in connections.items():
                self.mapping[a] = b
                self.mapping[b] = a

    def swap(self, c):
        """
        Returns the substituted character if there's a plugboard connection,
        or the same character if there's no mapping.
        """
        return self.mapping.get(c, c)

def vigenere_key_stream(message, key):
    """
    Generates a key stream for polyalphabetic offset calculation.
    Similar to Vigenère cipher approach, repeat the key to match the message length.
    """
    extended_key = (key * ((len(message)//len(key))+1))[:len(message)]
    return extended_key

def char_to_offset(ch):
    """
    Converts a character from our extended alphabet into an integer offset.
    The offset is the index of the character in the extended alphabet.
    """
    return alphabet.index(ch)

def lfsr_tap(state, taps=[0,1,3,4]):
    """
    A simple LFSR (Linear Feedback Shift Register) example:
    - 'state' is an integer representing the current LFSR state (assume 8-bit for simplicity).
    - 'taps' is a list of bit positions to XOR.
    
    Returns: (new_state, output_bit)
    new_state: the updated LFSR state after shifting
    output_bit: the bit shifted out of the LFSR (for use in creating pseudo-random patterns)
    """
    xor = 0
    for t in taps:
        xor ^= (state >> t) & 1
    # Extract LSB (output bit)
    out = state & 1
    # Shift right by 1 and insert XOR at the MSB
    state = (state >> 1) | (xor << 7)
    return state, out

# Example rotor wirings (fictitious, just extended by digits):
rotorI   = Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ0123456789")
rotorII  = Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE0123456789")
rotorIII = Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO0123456789")

# Two different reflector configurations:
reflectorA = "YRUHQSLDPXNGOKMIEBFZCWVJAT0123456789"
reflectorB = "FVPJIAOYEDRZXWGCTKUQSBNMHL0123456789"
reflectors = ReflectorSet([reflectorA, reflectorB])

# Example plugboard connections:
plugboard = Plugboard({'A':'D','P':'X','0':'9'})

class AdvancedEnigma:
    def __init__(self, rotors, reflectors, plugboard, key, lfsr_init=0b10101010):
        """
        An advanced Enigma-like machine with the following modifications:
        - Polyalphabetic approach: a key defines how much each rotor steps per character.
        - LFSR-based pseudo-random increments: adds complexity to rotor stepping.
        - Multiple reflectors: chosen based on key-derived offset.
        - Extended alphabet and complex stepping logic.

        rotors: List of Rotor objects
        reflectors: ReflectorSet object
        plugboard: Plugboard object
        key: A string used to generate a polyalphabetic stepping pattern (e.g. "AX3L9")
        lfsr_init: Initial state for the LFSR to generate pseudo-randomness.
        """
        self.rotors = rotors
        self.reflectors = reflectors
        self.plugboard = plugboard
        self.key = key
        self.lfsr_state = lfsr_init

    def encode_message(self, message):
        message = message.upper()
        result = []
        key_stream = vigenere_key_stream(message, self.key)

        for i, ch in enumerate(message):
            if ch not in alphabet:
                # Non-alphabetic characters pass through unchanged
                result.append(ch)
                continue

            # Polyalphabetic offset derived from the key character
            poly_offset = char_to_offset(key_stream[i])

            # Use LFSR to introduce additional complexity to the stepping
            # We'll iterate a few times to gather a small number used as extra steps
            step_increase = 0
            for _ in range(3):  # Take 3 bits from LFSR to form a small number
                self.lfsr_state, bit_out = lfsr_tap(self.lfsr_state)
                step_increase = (step_increase << 1) | bit_out
            # step_increase is now a small 0-7 number

            # Combine poly_offset and LFSR bits to determine total rotor steps
            total_step = (poly_offset + step_increase) % len(alphabet)

            # Advance rotors by different amounts:
            # - First rotor by total_step
            # - Second rotor by (total_step * 2) mod 36
            # - Third rotor by (total_step // 2) mod 36
            # This non-linear stepping reduces predictability.
            self.rotors[0].step(total_step)
            self.rotors[1].step((total_step * 2) % len(alphabet))
            self.rotors[2].step((total_step // 2) % len(alphabet))

            # Pass through plugboard (entry)
            c = self.plugboard.swap(ch)

            # Forward pass through rotors (simulating right-to-left flow)
            # Traditionally Enigma: right-most rotor first, but here we have a custom approach.
            for r in reversed(self.rotors):
                c = r.encode_forward(c)

            # Choose reflector based on poly_offset
            reflector_index = poly_offset % len(self.reflectors.reflectors)
            c = self.reflectors.reflect(c, reflector_index)

            # Backward pass through rotors (left-to-right)
            for r in self.rotors:
                c = r.encode_backward(c)

            # Pass through plugboard (exit)
            c = self.plugboard.swap(c)

            result.append(c)

        return "".join(result)

# Example usage:
key = "AX3L9"  # Polyalphabetic key
enigma = AdvancedEnigma([rotorI, rotorII, rotorIII], reflectors, plugboard, key)

plaintext = "HELLO WORLD 123"
cipher = enigma.encode_message(plaintext)
print("Cipher Text:", cipher)

# To decrypt, initialize a new machine with the SAME settings and key:
enigma2 = AdvancedEnigma([Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ0123456789"),
                          Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE0123456789"),
                          Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO0123456789")],
                         reflectors, Plugboard({'A':'D','P':'X','0':'9'}), key)

decrypted = enigma2.encode_message(cipher)
print("Decrypted Text:", decrypted)
