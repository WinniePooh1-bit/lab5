# Лаборатори №5: API систем тест — Postman ба Newman

* **Оюутны нэр:** М.Наранбат
* **Оюутны код:** B242270801
* **Node.js хувилбар (`node -v`):** `v26.7.0`
* **Newman хувилбар (`newman -v`):** `6.2.3`

---

## Тест Дизайн (Лекц 5-ын аргачлал)

### 1. Сонголт ба төлөөлөх утгын хүснэгт
| Сонголт (Parameter) | Эквивалент ангиуд / Сонголтууд | Төлөөлөх утгууд (Representative Values) |
| :--- | :--- | :--- |
| **studentID-гийн хүчинтэй байдал** | Идэвхтэй, Идэвхгүй, Байхгүй | `"B231234567"` (active), `"B239999999"` (inactive), байхгүй ID |
| **Оюутны үзсэн хичээлүүд** | Урьдач хангасан, Хангаагүй/Дутуу, Хоосон | `["CS201"]`, `[]` |
| **courseID-гийн хүчинтэй байдал** | Системд байгаа, Байхгүй | `"CS313"`, `"CS999"` |
| **Хичээлийн урьдач нөхцөл** | Шаардлагатай, Хоосон (Урьдачгүй) | `["CS201"]`, `[]` |

### 2. Спецификацийн хүснэгт (Тест кейсүүд болон давхар алдаанууд)
| № | Тестийн нэр / Спецификаци | Setup (PUT хүсэлтүүд) | POST /registrations өгөгдөл (Body) | Хүлээгдэх Статус | Хүлээгдэх Result (Хариу) |
|---|---|---|---|---|---|
| **1** | **Happy Path:** Амжилттай бүртгэл | Student: active, CS201<br>Course: prereq [CS201] | `{"studentID": "B231234567", "courseID": "CS313"}` | **201** | `{"result":"OK","registrationID":...}` |
| **2** | **Error - Талбар дутуу:** studentID байхгүй | — | `{"courseID": "CS313"}` | **400** | `{"result":"ERROR_BAD_REQUEST"}` |
| **3** | **Error - Оюутан байхгүй:** Системд бүртгэлгүй ID | Student: үүсгээгүй | `{"studentID": "B999999999", "courseID": "CS313"}` | **200** | `{"result":"ERROR_NO_STUDENT"}` |
| **4** | **Error - Идэвхгүй оюутан:** status = inactive | Student: inactive<br>Course: CS313 | `{"studentID": "B231234567", "courseID": "CS313"}` | **200** | `{"result":"ERROR_INACTIVE_STUDENT"}` |
| **5** | **Error - Хичээл байхгүй:** courseID бүртгэлгүй | Student: active<br>Course: үүсгээгүй | `{"studentID": "B231234567", "courseID": "CS999"}` | **200** | `{"result":"ERROR_NO_COURSE"}` |
| **6** | **Error - Урьдач нөхцөл дутуу:** Prerequisite дутуу | Student: active, coursesTaken: []<br>Course: prereq [CS201] | `{"studentID": "B231234567", "courseID": "CS313"}` | **200** | `{"result":"ERROR_PREREQUISITES","missing":["CS201"]}` |
| **7** | **Boundary - Урьдач нөхцөлгүй хичээл:** Prereq хоосон | Student: active, coursesTaken: []<br>Course: prereq [] | `{"studentID": "B231234567", "courseID": "CS313"}` | **201** | `{"result":"OK","registrationID":...}` |
| **8** | **Double Error - Идэвхгүй оюутан & Prereq дутуу** | Student: inactive, coursesTaken: []<br>Course: prereq [CS201] | `{"studentID": "B231234567", "courseID": "CS313"}` | **200** | `{"result":"ERROR_INACTIVE_STUDENT"}` |
| **9** | **Double Error - Байхгүй хичээл & Prereq дутуу** | Student: active, coursesTaken: []<br>Course: үүсгээгүй | `{"studentID": "B231234567", "courseID": "CS999"}` | **200** | `{"result":"ERROR_NO_COURSE"}` |
| **10** | **Task 5 - Нийтийн API (JSONPlaceholder):** GET users | GET `/users` | — | **200** | Array with user objects |

---

## Newman Автоматжуулалт ба Үр Дүн

* **Pass үр дүн (`results/newman-pass.txt`):** Assertions executed: 17, Failed: 0, Exit code: 0.
* **Fail үр дүн (`results/newman-fail.txt`):** Assertions failed ≥ 1, Exit code: 1.
* **Down үр дүн (`results/newman-down.txt`):** Сервер унтарсан үед `ECONNREFUSED` алдаа гарсан, Exit code: 1[cite: 2].
  > *Тайлбар:* `ECONNREFUSED` нь сервер асаалтгүй эсвэл холбогдож чадахгүй байгаа **интерфейсийн/сүлжээний алдаа** бөгөөд тест oracle-ийн логик алдаа биш юм[cite: 2].

---

## Task 5: Нийтийн API-ийн туршлага
`https://jsonplaceholder.typicode.com/users` руу GET хүсэлт явуулж шалгахад локал API-тай харьцуулахад ямар нэгэн setup (PUT) хийх шаардлагагүй, өгөгдөл нь шууд бэлэн байдгаараа хялбар байсан боловч серверийн төлөв болон өгөгдлийг бид өөрсдөө удирдах боломжгүй хязгаарлагдмал байлаа.

---

## Дүгнэлт

Энэхүү лабораторийн ажлаар Лекц 5-ын тест дизайны 5 алхмыг бодит REST API дээр бүрэн хэрэгжүүлж сурлаа. Системийн ин-мемори бүтэц болон олон төрлийн алдааны нөхцөлийг шалгахад тестийн бие даасан байдал (`test independence`) буюу тест бүр өөрийн гэсэн PUT setup-тай байх нь маш чухал болохыг туршлагаар ойлголоо. Давхар алдааны тохиолдлууд дээр серверийн шалгалтын дараалал ямар байх ёстойг тестээр нарийвчлан тогтоосон. Newman ашиглан CLI орчноос автомат тест гүйцэтгэж, CI quality gate зарчмын дагуу pass, fail болон down төлөвүүдийг амжилттай шалгаж баталгаажууллаа[cite: 2].
