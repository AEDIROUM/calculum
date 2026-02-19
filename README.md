# drp

Drop files or paste text, get a link instantly. **[Live →](https://drp.vicnas.me)**

```bash
pipx install drp-cli
drp setup && drp up "hello world"
```

## Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.com?referralCode=ZIdvo-)

1. Fork → Railway → connect repo → add PostgreSQL
2. Set env vars (see `.env.example`)
3. Start command:
   ```
   python manage.py createcachetable && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn project.wsgi --bind 0.0.0.0:$PORT
   ```
4. Create superuser via Railway shell: `python manage.py createsuperuser`

### Required vars
| Variable | Description |
|---|---|
| `SECRET_KEY` | Random secret |
| `DOMAIN` | Your domain, no `https://` |
| `DB_URL` | PostgreSQL URL |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary credentials |
| `CLOUDINARY_API_KEY` | |
| `CLOUDINARY_API_SECRET` | |

### Optional vars
| Variable | Description |
|---|---|
| `RESEND_API_KEY` | Enables email (password resets, broadcasts). Without it, emails print to console. |
| `DEFAULT_FROM_EMAIL` | Defaults to `noreply@<DOMAIN>` |
| `ADMIN_EMAIL` | Your email |
| `LEMONSQUEEZY_*` | Billing — leave blank to disable paid plans |

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate && python manage.py createcachetable
python manage.py runserver
```

## Plans

| | Anonymous | Free | Starter ($3/mo) | Pro ($8/mo) |
|---|---|---|---|---|
| Max file | 200 MB | 200 MB | 1 GB | 5 GB |
| Storage | — | — | 5 GB | 20 GB |
| Clipboard idle | 24h | 48h | explicit date | explicit date |
| Clipboard max lifetime | 7 days | 30 days | up to 1 year | up to 3 years |
| File expiry | 90 days | 90 days | explicit date | explicit date |
| Locked drops | ✗ | ✗ | ✓ | ✓ |

## License

Server: source-available, personal/internal use only. See [LICENSE](LICENSE) and [COMMERCIAL.md](COMMERCIAL.md).
CLI (`cli/`): MIT.