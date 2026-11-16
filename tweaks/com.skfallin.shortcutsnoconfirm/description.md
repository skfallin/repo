Lets **Shortcuts automations** run without the confirmation prompts iOS still shows when *Ask Before Running* is off.

The typical case: an automation that ends with **Shut Down**. The condition is met, but the phone sits on *Continue?* instead of turning off. With ShortcutsNoConfirm it just shuts down, even when locked.

### What it skips

- **Shut Down / Restart**: *Continue?* and the unlock request when locked
- **Secure Home accessories** (locks, gates, garage doors): confirmation and unlock request
- **App Intents** and **SiriKit** confirmations: answered *Yes*
- **Deleting** photos, files and other items
- **Deleting or sharing** large amounts of data

It does not touch *Ask Before Running*, privacy prompts (*Allow "…" to access …?*) or prompts your shortcut asks on purpose (*Show Alert*, *Ask for Input*, *Choose from Menu*).

### ⚠️ Read before enabling

With the switch on, **destructive actions run with no chance to cancel**. Check your automation conditions first, and test with an automation you can trigger right away.

### Setup

Open **Settings → ShortcutsNoConfirm**. The switch is on by default and changes apply immediately. Turn it off to get stock behaviour back without uninstalling.

### Status

Beta, **not yet tested on a device**. Every hooked class and selector was checked against the iOS 16.5.1 (20F75) binaries. Requires iOS 16.5.1, rootless (Dopamine), ElleKit and PreferenceLoader.

Bug reports: [GitHub issues](https://github.com/skfallin/ShortcutsNoConfirm/issues) · MIT license
