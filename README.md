# WorkBuddy Automation Suite

Suite otomatisasi login / registrasi WorkBuddy (`workbuddy.ai` — Tencent AI Workspace) via GitHub OAuth, ekstraksi session cookies, dan auto-claim **250 welcome credits**.

## 🚀 Fitur Utama

- **Autonomous GitHub OAuth Broker Flow**: Melewati alur login WorkBuddy Keycloak (`copilot` realm) dan mengotorisasi izin GitHub secara headless dengan Camoufox.
- **Dukungan Kredensial Multi-Mode**:
  1. Login via `user_session` cookie GitHub (langsung tembus tanpa captcha / tanpa 2FA).
  2. Login via `username` + `password` + RFC 6238 TOTP (zero external dependency).
  3. Batch processing via file `accounts.txt`.
- **API Client WorkBuddy Terintegrasi**: Menginspeksi saldo kuota `/billing/meter/get-user-resource` dan limit cloud agent `/v2/user/cloudagent/quota`.

## 💻 Cara Penggunaan

### 1. Login via Cookie `user_session` GitHub (Paling Cepat & Anti-Captcha)
```bash
./run.sh login -c <COOKIE_USER_SESSION_GITHUB>
```

### 2. Login via Akun GitHub (Username + Password)
```bash
# Tanpa 2FA
./run.sh login -u your_username -p your_password

# Dengan 2FA TOTP (masukkan base32 secret)
./run.sh login -u your_username -p your_password -t JBSWY3DPEHPK3PXP
```

### 3. Mode Visual Headed (Debug)
```bash
./run.sh login -u your_username -p your_password --headed
```

### 4. Daftar Akun & Saldo Tersimpan
```bash
./run.sh list
```
