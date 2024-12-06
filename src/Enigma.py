import string

class Rotor:
    def __init__(self, wiring, notch, ring_setting=0, position=0):
        self.alphabet = string.ascii_uppercase
        self.wiring = wiring
        self.notch = notch
        self.ring_setting = ring_setting
        self.position = position

    def encode_forward(self, c):
        offset = (self.position - self.ring_setting) % 26
        idx = (self.alphabet.index(c) + offset) % 26
        return self.wiring[idx]

    def encode_backward(self, c):
        offset = (self.position - self.ring_setting) % 26
        idx = self.wiring.index(c)
        return self.alphabet[(idx - offset) % 26]

    def step(self):
        self.position = (self.position + 1) % 26

    def at_notch(self):
        current_letter = self.alphabet[self.position]
        return current_letter == self.notch

class Reflector:
    def __init__(self, wiring):
        self.alphabet = string.ascii_uppercase
        self.wiring = wiring

    def reflect(self, c):
        idx = self.alphabet.index(c)
        return self.wiring[idx]

class Plugboard:
    def __init__(self, connections=None):
        self.alphabet = string.ascii_uppercase
        self.mapping = {ch: ch for ch in self.alphabet}
        if connections:
            for a, b in connections.items():
                self.mapping[a] = b
                self.mapping[b] = a

    def swap(self, c):
        return self.mapping.get(c, c)

class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard):
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard

    def step_rotors(self):
        # Step mekanizması
        if self.rotors[2].at_notch():
            if self.rotors[1].at_notch():
                self.rotors[0].step()
            self.rotors[1].step()
        self.rotors[2].step()

    def encode_letter(self, c):
        if c not in string.ascii_uppercase:
            return c
        self.step_rotors()
        c = self.plugboard.swap(c)
        for r in reversed(self.rotors):
            c = r.encode_forward(c)
        c = self.reflector.reflect(c)
        for r in self.rotors:
            c = r.encode_backward(c)
        c = self.plugboard.swap(c)
        return c

    def encode_message(self, msg):
        msg = msg.upper()
        encoded = ""
        for ch in msg:
            if ch in string.ascii_uppercase:
                encoded += self.encode_letter(ch)
            else:
                encoded += ch
        return encoded

# Rotor ayarları (Örnek)
rotorI   = Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q", ring_setting=0, position=0)
rotorII  = Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E", ring_setting=0, position=0)
rotorIII = Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V", ring_setting=0, position=0)

reflectorB = Reflector("YRUHQSLDPXNGOKMIEBFZCWVJAT")
plugboard = Plugboard({'A':'D','P':'X'})

# Enigma makinesi oluştur
enigma = EnigmaMachine([rotorI, rotorII, rotorIII], reflectorB, plugboard)

# Örnek metin
plaintext = "HELLO WORLD"

# Şifreli metni üret
ciphertext = enigma.encode_message(plaintext)
print("Şifreli Metin:", ciphertext)

# Çözümleme için aynı ayarlarla yeni bir Enigma örneği oluşturuyoruz.
# Dikkat: Rotorların başlangıç konumlarını orijinalle aynı yapmamız gerekir.
rotorI2   = Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q", ring_setting=0, position=0)
rotorII2  = Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E", ring_setting=0, position=0)
rotorIII2 = Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V", ring_setting=0, position=0)
plugboard2 = Plugboard({'A':'D','P':'X'})
enigma_decrypt = EnigmaMachine([rotorI2, rotorII2, rotorIII2], reflectorB, plugboard2)

# Şifreli metni çöz
decrypted = enigma_decrypt.encode_message(ciphertext)
print("Çözülen Metin:", decrypted)
