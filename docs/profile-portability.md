# Profile Portability

Use the hermes-stack helpers for this profile.

## VPS export

```bash
cd /home/hermes/work/hermes-stack
bash scripts/export-profile.sh --profile ai-lab
```

This creates a portable bundle under the synced exports directory.

## Mac import

After cloning `hermes-stack` on the Mac and bootstrapping the machine:

```bash
cd ~/path/to/hermes-stack
bash scripts/import-profile.sh --archive <bundle.tar.gz> --service-mode remote --gateway skip
```

## Machine bootstrap

VPS:
```bash
cd /home/hermes/work/hermes-stack
bash scripts/bootstrap-machine.sh --env-id vps --service-mode auto
```

Mac:
```bash
cd ~/path/to/hermes-stack
bash scripts/bootstrap-machine.sh --env-id macbook --service-mode remote
```

## Why prefer this over raw Hermes export/import

These repo helpers preserve the stack's shared/profile split more faithfully:
- shared SOUL source files
- rendered environment context
- profile-local Hindsight bank wiring
- non-secret env templates
- references to synced backups
