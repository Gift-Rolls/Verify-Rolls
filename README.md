# Provably-Fair Verification Tool

This folder contains `verify.py` – a standalone script that allows **any player** to independently prove that a GameRoll round was fair and that the server did not manipulate the result after seeing the bets. -> `verify.py` is a minimal **one-file** script (no external dependencies) that lets *any* player double-check a completed GameRoll round.  
It answers two simple questions:

1. Did the revealed **Seed** really match the publicly committed **Hash**?
2. Given that Seed and the exact list of bets, is the chosen winner deterministic and correct?

---
## Quick start
1. Open the finished round in the GameRoll bot or web interface and click **Legit check → Download bets.json**.  
   You will get a file with every player's stake in TON.
2. Copy the **Seed** and **Hash** values shown in the same Legit-check window.
3. Run the script:
```bash
python scripts/verify.py --seed 4f7b899d0a0e8611f... --hash 8e1c8e61f5f4c7a9... --bets bets.json
```
If the round is fair you will see a confirmation together with the winning ticket and Telegram account.

---
## How it works
1. **Commit phase** – When a new round starts the server generates a 32-byte random *Seed* and immediately publishes its SHA-256 hash (the *Hash* field). The Seed itself stays secret until the round finishes.
2. **Betting phase** – Players send gifts. Each 0.01 TON is treated as **one ticket**.
3. **Reveal phase** – After the countdown the server reveals the original *Seed*. Anyone can verify that `sha256(Seed) == Hash` published earlier.
4. **Winner selection** – The SHA-256 digest of the Seed is interpreted as a big integer. Taking it modulo the total number of tickets gives a deterministic winning ticket. Scanning the ordered ticket list yields the winner.

Because the algorithm is fully deterministic, the same Seed + bets will *always* produce the exact same winner.

---
## Requirements
* Python ≥ 3.9 (the standard library is enough).

---
## `bets.json` format
The file downloaded from **Legit check** (or fetched via `/game-roll/info` API) looks like this:
```json
{
  "123456": 3.00,
  "987654": { "amount": 7.21, "telegram_username": "bob" }
}
```
Rules:
* Amounts have at most two fractional digits (0.01 TON per ticket).
* You may optionally include `telegram_username` – it is only used for prettier output.

---
## Troubleshooting
* **`HASH mismatch – seed has been tampered with`**  
  The revealed seed does not correspond to the commitment. The round is invalid.
* **`The round contains no tickets`**  
  Bets file is empty or all amounts are non-positive.
* **`Stake ... is not a valid number`**  
  Incorrect JSON format or non-numeric value.

---
## License
MIT 

---

# Проверка честности GameRoll

`verify.py` — минимальный скрипт без внешних зависимостей, который позволяет **любой** стороне проверить честность завершённого раунда GameRoll.

Он отвечает на два вопроса:

1. Совпадает ли раскрытый **Seed** с заранее опубликованным **Hash**?
2. При тех же ставках выдаёт ли алгоритм того же победителя?

---
## Быстрый старт
1. Откройте завершённый раунд в боте или на сайте GameRoll и нажмите **Legit check → Download bets.json** — получите файл со ставками всех игроков.
2. Скопируйте значения **Seed** и **Hash** из того же окна Legit-check.
3. Запустите скрипт:
```bash
python scripts/verify.py --seed 4f7b899d0a0e8611f... --hash 8e1c8e61f5f4c7a9... --bets bets.json
```
При корректном раунде вы увидите сообщение об успехе и информацию о победителе.

---
## Как это работает
1. **Commit-фаза** — сервер генерирует случайный 32-байтный *Seed* и тут же публикует его SHA-256 хэш (**Hash**).
2. **Ставки** — каждый подарок стоимостью 0,01 TON считаетcя одним «билетом».
3. **Reveal-фаза** — после таймера сервер раскрывает исходный *Seed*, любой может проверить `sha256(Seed) == Hash`.
4. **Выбор победителя** — SHA-256 от Seed интерпретируется как большое число. Остаток от деления на общее количество билетов даёт выигрышный билет. Проход по упорядоченному списку билетов определяет победителя.

---
## Требования
* Python ≥ 3.9 (стандартная библиотека достаточно).

---
## Формат `bets.json`
```json
{
  "123456": 3.00,
  "987654": { "amount": 7.21, "telegram_username": "bob" }
}
```
• Не более двух знаков после запятой (0.01 TON = один билет).  
• `telegram_username` необязателен и нужен лишь для красивого вывода.

---
## Диагностика ошибок
* **`HASH mismatch – seed has been tampered with`** — Seed не соответствует Hash, раунд недействителен.
* **`The round contains no tickets`** — Нет билетов (пустые или нулевые ставки).
* **`Stake ... is not a valid number`** — Неверный JSON или нечисловое значение.

---
## Лицензия
MIT 
