# Enigma Makinesi Simülasyonu

Bu proje, İkinci Dünya Savaşı sırasında Almanlar tarafından kullanılan Enigma şifreleme makinesinin temel prensiplerini Python ile basitleştirilmiş bir şekilde simüle eder. Gerçek Enigma son derece karmaşık günlük ayarlamalar ve prosedürlere sahip olsa da, bu örnek kod Enigma’nın temel mantığını anlamaya yardımcı olacaktır.

## Genel Bakış

Enigma makinesi bir **substitüsyon şifreleme cihazı**dır. Basılan her harf, **plugboard**, **rotorlar** ve **reflektör** üzerinden geçerek farklı bir harfe dönüşür. Ancak Enigma’nın en önemli özelliği, aynı ayarlarla çalıştırıldığında şifrelenmiş metni tekrar giriş olarak vererek orijinal metne ulaşabilmenizdir. Yani şifreleme ve deşifreleme aynı mantıkla, aynı makine ayarlarıyla yapılır.

### Veri Akışı (Bir Harf İçin)

1. **Giriş Harfi**: Operatör bir harfe basar (örneğin `H`).
2. **Plugboard (Fiş Tahtası)**: Harf, giriş ve çıkışta fiş tahtasından geçer. Fiş tahtasında belirli harf çiftleri birbirine eşleştirilmiştir.  
   - Örneğin, `A` ve `D` eşleştirilmişse, `A` girdiğinde `D` çıkar.
   - Eğer girdi harfi plugboard’da eşleştirilmemişse aynı kalır.
3. **Rotorların Adımlanması**: Her harf girişinden önce, rotorlar bir saat sayacı gibi adım atarlar.  
   - Sağ rotor her harfte bir adım döner.  
   - Belirli harf konumlarında orta rotor devreye girer ve bazen sol rotor da ilerler.  
   - Bu mekanizma, her harf için şifrelemenin değişmesini sağlar.
4. **İleri Yönde Rotorlardan Geçiş (Sağdan Sola)**: Harf, sağ rotordan girer ve iç kablolamaya bağlı olarak başka bir harfe dönüşür, sonra ortadaki rotora geçer, orada da dönüşür, en son sol rotora girerek başka bir harfle çıkar.  
   - Her rotor, bir permütasyon tablosuna sahiptir.  
   - Rotorun pozisyonu, giriş harfine eklenecek bir offset (kayma) yaratır.
5. **Reflektör**: Sol rotordan çıkan harf, reflektöre gider.  
   - Reflektör, harfleri çiftler halinde eşleştirir.  
   - Harf, reflektörden geri dönerken başka bir harfe dönüşür. Bu dönüş tek yönlü değil, simetriktir: A → Y ise Y → A’dır.
6. **Geri Yönde Rotorlardan Geçiş (Soldan Sağa)**: Reflektörden dönen sinyal bu kez soldan sağa (ters istikamette) rotorların içinden geçer.  
   - Bu aşamada rotorlar `encode_backward` metoduyla harfi çözerek başka bir harfe dönüştürür.  
   - Aynı rotorlar ama ters yönde geçtiğimiz için dönüşüm yine değişir.
7. **Tekrar Plugboard**: Çıkan harf tekrar plugboard’dan geçerek son bir dönüşüme uğrar (varsa).
8. **Çıkış Harfi**: Sonuç olarak elde ettiğiniz harf, şifreli metnin karakterini oluşturur.

Bu sürecin sonucu: Girişteki harf, karmaşık bir subtitüsyon sonucu farklı bir harfle çıkar. Her harfte rotorların adımlanması nedeniyle, aynı harf girişine karşılık her seferinde farklı bir şifreli harf elde etmek mümkündür.

## Örnek Akış Şeması

Aşağıda bir harfin şifrelenme sürecini özetleyen bir akış diyagramı verilmiştir:


A[Başlangıç: Giriş Harfi] --> B[Plugboard Giriş]
B -->|Eşleşme Yoksa Harf Değişmez| C[Rotors Step (Adımlama)]
B -->|Eşleşme Varsa Harf Değişir| C

C --> D[Rotordan Geçiş (İleri: Sağ->Sol)]
D --> E[Reflektör]
E --> F[Rotordan Geçiş (Geri: Sol->Sağ)]
F --> G[Plugboard Çıkış]

G --> H[Çıkış Harfi]
H --> I[Bitiş]
