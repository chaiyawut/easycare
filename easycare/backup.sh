DJANGO_ENV=production ./manage.py dumpdata frontend > backup/frontend.json
git add -A
git commit -m "backup"
git push
