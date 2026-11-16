A **software lock-screen PIN** for rootless arm64e iOS 16.5.1, for devices that can't use the native passcode, such as A12/A13 iPhones after a tethered downgrade.

Based on [FakePass by alexia](https://github.com/lunaynx/fakepass), rebuilt for the modern arm64e ABI and rootless packaging.

### ⚠️ What it is not

This PIN only blocks ordinary access through the lock screen **while tweak injection is active**. It does **not** enable the native passcode, add data encryption, restore Face ID or enable Apple Pay. Safe Mode, a hidden jailbreak or removing the tweak bypasses it. Don't rely on it to protect sensitive data.

### What's new compared to FakePass

- Rebuilt for arm64e and rootless
- No PIN, hash or salt logging
- No device-erasure logic or permanent lockout; temporary throttling kept
- Changing or removing a PIN now requires the correct old PIN (beta 2)
- Preferences cleaned up on removal

### Before installing

1. Remove other passcode or app-lock tweaks (original FakePass, A-Shields, Checkl0ck, Lockdown, BioProtect…).
2. Install **libSandy 1.1.6+** from its official source, `https://opa334.github.io`.
3. Keep SSH access available so you can remove the tweak if something breaks.

### Setup

1. Open **Settings → Fakepass Reborn** and leave *Lock after respring* on.
2. Go to **Settings → Face ID & Passcode**. Continue **only** if the button says **(Fakepass Reborn)**. If it doesn't, stop: enabling the native passcode on a downgrade can cause a SEP panic.
3. Set a six-digit PIN, then lock the screen and check that the correct PIN works and a wrong one is rejected.

### Status

Beta. The prototype was tested on an iPhone XS Max, iOS 16.5.1, Dopamine 3.0.9-fix rootless. Other models and versions are not validated.

[Source code](https://github.com/skfallin/FakepassReborn) · [Bug reports](https://github.com/skfallin/FakepassReborn/issues) · MIT license
