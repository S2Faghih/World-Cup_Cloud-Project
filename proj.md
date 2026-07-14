```markdown
# مبانی رایانش ابری

**دانشگاه صنعتی امیرکبیر – دانشکده مهندسی کامپیوتر**  
نیمسال دوم ۱۴۰۴-۱۴۰۵

## فاز اول پروژه پایانی  
**تحلیل لاگ جام جهانی با MapReduce و Nginx**

استاد درس: دکتر جوادی  
 مهرداد شیخ عباسی  
 محمد هادی ستاک  

**زمان تحویل:** جمعه ۲ مرداد ۱۴۰۵، ساعت ۲۳:۵۹  

**مورد تحویلی:**  
نام فایل زیپ نهایی باید مطابق قالب `CC_Project_Phase1_StudentID1_StudentID2.zip` باشد.  
در این نام‌گذاری، `StudentID1` و `StudentID2` باید با شماره دانشجویی دو عضو گروه جایگزین شوند. برای مثال، اگر شماره دانشجویی دو عضو گروه ۴۰۱۲۳۴۵۶ و ۴۰۲۳۴۵۶۷ باشد، نام فایل زیپ باید به صورت `CC_Project_Phase1_40123456_40234567.zip` انتخاب شود.

---

## ۱. هدف فاز اول

هدف فاز اول پروژه، ساخت یک سامانه ساده برای تولید و تحلیل لاگ است. در این فاز، دانشجوها باید چند سرویس اجرا کنند، با یک برنامه تولیدکننده ترافیک به آن‌ها درخواست بفرستند، لاگ‌های Nginx را با Python ساده پردازش کنند و در پایان چند خروجی تحلیلی مشخص با کدهای Hadoop Streaming و Python تولیدشده را بسازند.

در این فاز، تمرکز اصلی روی مفاهیم زیر است:

- اجرای چند سرویس ساده با Docker و Docker Compose؛
- استفاده از Nginx به عنوان reverse proxy یا API Gateway؛
- تولید ترافیک و تولید لاگ قابل تحلیل؛
- طراحی schema مشخص برای لاگ‌ها؛
- پردازش batch لاگ‌ها با MapReduce؛
- تولید خروجی‌های تحلیلی عمومی و سناریومحور؛
- انجام تحلیل real-time با Spark Structured Streaming (به صورت امتیازی).

## ۲. سناریوی پروژه

سناریوی این فاز، تحلیل لاگ یک سامانه ساده اطلاعات جام جهانی است. در این سامانه، کاربران از کشورهای مختلف به سرویس‌های مختلف درخواست می‌فرستند و در باره بازی‌ها، تیم‌ها و ورزشگاه‌ها اطلاعات می‌گیرند.

سامانه شامل سه سرویس ساده است:

- `match-service`: دریافت تاریخ و برگرداندن بازی‌های آن روز؛
- `team-service`: دریافت نام تیم و برگرداندن اطلاعات ساده تیم؛
- `stadium-service`: دریافت نام ورزشگاه یا شهر و برگرداندن اطلاعات مربوط به آن.

> **نکته:** کد پایه سه سرویس match-service، team-service و stadium-service در اختیار دانشجوها قرار می‌گیرد. این کد پایه فقط برای داشتن endpoint‌های اولیه است و بخش‌های مربوط به تولید لاگ با ساختاریافته و ثبت فیلدهای مرتبط با موجودیت در رکورد لاگ، با مقدار `TODO` مشخص شده و باید تکمیل شوند. تکمیل همین بخش‌های ناقص، نوشتن Dockerfile، تنظیم Nginx، نوشتن traffic generator و پیاده‌سازی MapReduce بر عهده دانشجوهاست.

---

## ۳. معماری مورد انتظار

تمام درخواست‌ها باید ابتدا به Nginx ارسال شوند و سپس Nginx آن‌ها را به سرویس مناسب منتقل کند. در اجرای نهایی، traffic generator نباید مستقیماً به سرویس‌های backend درخواست بفرستد.

مسیر صحیح درخواست‌ها به شکل زیر است:

```
traffic generator ---> Nginx ---> backend services
                          |              |
                          v              v
                 nginx_access.log   service logs (per service)
```

در این معماری دو دسته لاگ تولید می‌شود: Nginx gateway log برای تحلیل‌های عمومی و لاگ اختصاصی هر سرویس برای تحلیل‌های مخصوص سرویس‌ها. این جداسازی در بخش «فرمت لاگ‌ها» با جزئیات توضیح داده می‌شود.

ساختار کلی اجزای پروژه باید شامل موارد زیر باشد:

- سه سرویس Python ساده که هرکدام لاگ ساختاریافته خود را می‌نویسند؛
- Nginx به عنوان reverse proxy و تولیدکننده `nginx_access.log`؛
- یک برنامه Python برای تولید ترافیک (فقط نقش کاربر آزمایشی)؛
- Nginx gateway log برای تحلیل‌های عمومی؛
- لاگ‌های اختصاصی سرویس‌ها برای تحلیل‌های مخصوص سرویس‌ها؛
- کدهای MapReduce با Hadoop Streaming؛
- خروجی‌های نهایی تحلیل.

---

## ۴. سرویس‌های backend

هر گروه باید سه سرویس ساده Python داشته باشد. استفاده از Flask یا FastAPI آزاد است، اما همه سرویس‌ها باید قابل اجرا داخل Docker باشند.

### ۴.۱. سرویس match-service

این سرویس با گرفتن یک تاریخ، بازی‌های آن روز را برمی‌گرداند.

نمونه endpoint:
```
GET /api/matches?date=2026-06-25
```

رفتارهای مورد انتظار:
- برای تاریخ‌های معتبر، پاسخ موفق برگرداند؛
- برای تاریخ نامعتبر یا بدون بازی، پاسخ مناسب با status code مشخص برگرداند؛
- در برخی درخواست‌ها بتواند پاسخ کندتر تولید کند تا تحلیل response time معنی‌دار شود.

### ۴.۲. سرویس team-service

این سرویس با گرفتن نام یک تیم، اطلاعات ساده‌ای درباره آن تیم برمی‌گرداند.

نمونه endpoint:
```
GET /api/teams?name=Argentina
```

رفتارهای مورد انتظار:
- برای تیم‌های موجود، پاسخ موفق برگرداند؛
- برای تیم‌های ناموجود، پاسخ خطای مناسب برگرداند؛
- داده‌ها به اندازه‌ای متنوع باشند که بتوان محبوبیت تیم‌ها را از روی تعداد درخواست‌ها تحلیل کرد.

### ۴.۳. سرویس stadium-service

این سرویس با گرفتن نام ورزشگاه یا شهر، اطلاعات ساده مربوط به آن را برمی‌گرداند.

نمونه endpoint:
```
GET /api/stadiums?name=New York New Jersey Stadium
GET /api/stadiums?city=New York New Jersey
```

رفتارهای مورد انتظار:
- برای ورزشگاه‌ها یا شهرهای معتبر، پاسخ موفق برگرداند؛
- برای ورودی نامعتبر، پاسخ خطای مناسب برگرداند؛
- امکان تحلیل پرجست‌وجوترین ورزشگاه یا شهر وجود داشته باشد.

### ۴.۴. داکرایز کردن سرویس‌ها

برای هر سه سرویس باید یک Dockerfile مستقل نوشته شود تا سرویس داخل کانتینر اجرا شود. انتظار می‌رود هر سرویس حداقل این موارد را داشته باشد:

- فایل `requirements.txt` برای وابستگی‌های Python؛
- فایل Dockerfile مستقل؛
- اجرای سرویس روی `0.0.0.0` تا از داخل شبکه Docker Compose قابل دسترسی باشد؛
- پورت داخلی مشخص برای هر سرویس؛
- عدم وابستگی به مسیرهای مطلق روی سیستم شخصی دانشجو؛
- نوشتن یک لاگ ساختاریافته اختصاصی به صورت JSON Lines در مسیر `data/service_logs/`؛
- استفاده از مقدارهای `X-Request-ID`، `X-Client-Country`، `X-Scenario` که Nginx به سرویس منتقل می‌کند، در رکورد لاگ ساختاریافته.

> **نکته:** کد پایه سه سرویس match-service، team-service و stadium-service در اختیار دانشجوها قرار می‌گیرد، اما بخش لاگ‌گذاری تحلیلی آماده نیست و باید توسط گروه تکمیل شود. در این پروژه دو دسته لاگ داریم: `nginx_access.log` که Nginx تولید می‌کند و برای تحلیل‌های عمومی (gateway-level) به کار می‌رود؛ و لاگ اختصاصی هر سرویس که حاوی اطلاعات مربوط به موجودیت (`entity_type` و `entity_value`) است و برای تحلیل‌های مخصوص سرویس‌ها استفاده می‌شود. traffic generator فقط نقش کاربر آزمایشی را دارد و لاگ آن مبنای تحلیل نیست.

---

## ۵. تنظیم Nginx

Nginx باید جلوی سه سرویس قرار بگیرد و بر اساس مسیر درخواست، آن را به سرویس مناسب منتقل کند. برای مثال، در پروژه واقعی شما مسیرهای مربوط به بازی‌ها، تیم‌ها و ورزشگاه‌ها باید به سرویس متناظر ارسال شوند؛ اما در این بخش، برای هدف آموزشی، یک مثال فرضی و ساده توضیح داده می‌شود تا ساختار کانفیگ مشخص شود بدون اینکه جواب مستقیم پروژه داده شود.

همه درخواست‌ها باید به دست Nginx برسند؛ همچنین Nginx gateway log باید از Nginx به دست آید و لاگ‌های سرویس‌ها برای تحلیل‌های مخصوص سرویس‌ها مورد استفاده قرار می‌گیرند.

> **توجه:** در اجرای نهایی، اگر traffic generator مستقیماً به سرویس‌های backend درخواست بفرستد و Nginx دور زده شود، اجرای پروژه ناقص محسوب می‌شود.

### ۵.۱. نمونه آموزشی کانفیگ و توضیح دستورهای Nginx

نمونه زیر مربوط به یک پروژه فرضی است که دو سرویس `service-a` و `service-b` دارد. دانشجوها باید همین ایده را برای مسیرها و سرویس‌های پروژه خودشان پیاده‌سازی کنند.

```nginx
events {
}

http {
    upstream service_a_upstream {
        server service-a:8000;
    }

    upstream service_b_upstream {
        server service-b:8000;
    }

    log_format json_logs escape=json
        '{"timestamp":"$time_iso8601",'
        '"request_id":"$http_x_request_id",'
        '"client_ip":"$remote_addr",'
        '"client_country":"$http_x_client_country",'
        '"scenario":"$http_x_scenario",'
        '"method":"$request_method",'
        '"path":"$request_uri",'
        '"service":"$target_service",'
        '"status_code":"$status",'
        '"request_time_sec":"$request_time",'
        '"user_agent":"$http_user_agent"}';

    access_log /var/log/nginx/nginx_access.log json_logs;

    server {
        listen 80;
        set $target_service "unknown";

        location /api/a {
            set $target_service service-a;
            proxy_pass http://service_a_upstream;
            proxy_set_header X-Request-ID $http_x_request_id;
            proxy_set_header X-Client-Country $http_x_client_country;
            proxy_set_header X-Scenario $http_x_scenario;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /api/b {
            set $target_service service-b;
            proxy_pass http://service_b_upstream;
            proxy_set_header X-Request-ID $http_x_request_id;
            proxy_set_header X-Client-Country $http_x_client_country;
            proxy_set_header X-Scenario $http_x_scenario;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

**توضیح دستورهای مهم:**

- `events`: بخش پایه Nginx برای تنظیم اتصال (حداقلی است).
- `http`: همه تنظیمات مربوط به درخواست‌های HTTP داخل این بخش قرار می‌گیرد.
- `upstream`: برای تعریف مقصدهای داخلی استفاده می‌شود. وقتی سرویس‌ها با Docker Compose اجرا شوند، نام سرویس‌ها همان نام‌های `service-a` در `docker-compose.yml` هستند. `server service-a:8000` یعنی درخواست‌ها به سرویس `service-a` روی پورت داخلی ۸۰۰۰ فرستاده شوند.
- `log_format`: شکل لاگ را مشخص می‌کند. در این پروژه باید لاگ ساختاریافته JSON باشد تا قابل پردازش باشد. `escape=json` برای خروجی JSON مناسب کمک می‌کند.
- `access_log`: مسیر ذخیره لاگ و فرمت آن را مشخص می‌کند. این فایل ورودی تحلیل‌های عمومی با MapReduce است.
- `server listen 80`: مشخص می‌کند Nginx داخل کانتینر روی پورت ۸۰ گوش می‌دهد. این نگاشت پورت به هاست باید در `docker-compose.yml` انجام شود.
- `location`: مسیرهای مختلف را جدا می‌کند و هر مسیر را به سرویس مناسب می‌فرستد.
- `proxy_set_header`: هدرهای مهم مثل request_id، کشور، سناریو را به سرویس مقصد منتقل می‌کند.
- `$request_time`: زمان پردازش درخواست در Nginx را بر حسب ثانیه نشان می‌دهد.

> **نکته:** نمونه بالا یک `nginx.conf` کامل است که شامل بلوک‌های `http` و `events` است. بنابراین در `docker-compose.yml` باید این فایل را به مسیر `/etc/nginx/nginx.conf` متصل کنید (mount کنید)، نه داخل `conf.d/`؛ در غیر این صورت Nginx اجرا نمی‌شود. همچنین باید پورت کانتینر را به هاست نگاه کنید، مثلاً `ports: ["8080:80"]`.

### ۵.۲. مسیر اجرا و تست Nginx

پس از تکمیل Dockerfile‌ها و `docker-compose.yml` و `nginx.conf`، سرویس‌ها را اجرا کنید:

```bash
docker compose up --build -d
```

وضعیت کانتینرها را بررسی کنید:

```bash
docker compose ps
```

برای تست درستی کانفیگ Nginx:

```bash
docker compose exec nginx nginx -t
```

اگر کانفیگ را تغییر دادید و نخواستید کل سیستم را restart کنید:

```bash
docker compose exec nginx nginx -s reload
```

برای تست دستی یک درخواست، حتماً به Nginx درخواست بفرستید، نه مستقیم به backend. نمونه زیر (فقط مثال است و باید با یکی از مسیرهای پروژه خودتان جایگزین شود):

```bash
curl -H "X-Request-ID: test-001" \
     -H "X-Client-Country: Iran" \
     -H "X-Scenario: manual-test" \
     "http://localhost:8080/<PROJECT_ENDPOINT>"
```

برای مشاهده لاگ تولیدشده:

```bash
docker compose exec nginx sh -c "tail -n 5 /var/log/nginx/nginx_access.log"
```

اگر مسیر لاگ را با Nginx به سیستم میزبان متصل کرده‌اید (volume mount)، می‌توانید همان فایل را از روی هاست نیز مشاهده کنید:

```bash
tail -n 5 data/nginx/nginx_access.log
```

**نتیجه مورد انتظار:**  
بعد از اجرای `curl`، باید یک خط جدید در `nginx_access.log` دیده شود. اگر `service`، `client_country` و `path` در لاگ نیامده باشند، کانفیگ لاگ کامل نیست.

> **توجه:** برای شروع یک اجرای تمیز، فایل لاگ Nginx را حذف کنید. اگر با volume به هاست متصل کرده‌اید، حذف مستقیم فایل ممکن است باعث شود Nginx به فایل قدیمی بنویسد. برای پاک‌سازی امن، فایل را `truncate` کنید یا Nginx را `restart` کنید.

---

## ۶. تولید ترافیک

دانشجوها باید یک برنامه Python بنویسند که نقش کاربرهای واقعی را بازی کند و برای تولید ترافیک درخواست بفرستد.

این برنامه باید هنگام ارسال هر درخواست، دست کم هدرهای زیر را تنظیم کند:

- `X-Request-ID: req_000001`
- `X-Client-Country: Iran`
- `X-Scenario: normal`

فیلد `X-Client-Country` برای تحلیل‌هایی مانند «هر کشور بیشتر طرفدار کدام تیم است» استفاده می‌شود. تشخیص کشور از روی IP در این پروژه الزم نیست.

ترافیک تولیدشده نباید به عنوان منبع اصلی تحلیل MapReduce استفاده شود. این برنامه فقط برای تولید درخواست و تست سیستم است. اگر دانشجو برای debug یک فایل کمکی مثل `generator_trace.csv` تولید کند، آن فایل نباید جایگزین `nginx_access.log` شود و نباید مبنای خروجی‌های اصلی MapReduce باشد.

### ۶.۱. سناریوهای اجباری ترافیک

ترافیک‌generator باید سناریوهای زیر را تولید کند:

- درخواست‌های عادی به هر سه سرویس؛
- درخواست به تیم‌ها، تاریخ‌ها یا ورزشگاه‌های مختلف؛
- درخواست با ورودی نامعتبر که خطای 4xx تولید کند؛
- درخواست‌هایی که باعث خطای 5xx شوند؛
- ترافیک نامتوازن، مثلاً درخواست بیشتر برای یک تیم، یک روز یا یک ورزشگاه خاص؛
- درخواست از چند کشور مختلف، با مقدارهای متفاوت در `X-Client-Country`.

### ۶.۲. حجم داده

برای تست اولیه، اجرای پروژه با تعداد کم درخواست مجاز است؛ اما خروجی نهایی باید با حجم کافی تولید شود:

- **Debug run:** حداقل ۱۰۰۰ درخواست
- **Final run:** حداقل ۱۰۰٬۰۰۰ درخواست

در اجرای نهایی، داده‌ها باید به اندازه‌ای متنوع باشند (endpoint‌ها، کشورها، تیم‌ها، تاریخ‌ها، ورزشگاه‌ها) که تفاوت بین سرویس‌ها و ورزشگاه‌ها در خروجی‌ها قابل مشاهده باشد.

---

## ۷. فرمت لاگ‌ها

در این پروژه دو دسته لاگ برای تحلیل داریم:

- `nginx_access.log`: Nginx gateway log که همه درخواست‌های عبوری از Nginx را ثبت می‌کند و مبنای تحلیل‌های عمومی است.
- لاگ‌های اختصاصی هر سرویس در مسیر `data/service_logs/` که مبنای تحلیل‌های مخصوص سرویس‌ها هستند.

### ۷.۱. فرمت `nginx_access.log`

پیشنهاد می‌شود لاگ Nginx به صورت JSON Lines ذخیره شود؛ یعنی هر خط یک JSON مستقل باشد.

**فیلدهای اجباری:**

| فیلد | توضیح |
|------|-------|
| `timestamp` | زمان درخواست |
| `request_id` | از هدر X-Request-ID |
| `client_ip` | IP کلاینت |
| `client_country` | از هدر X-Client-Country |
| `scenario` | از هدر X-Scenario |
| `method` | متد HTTP |
| `path` | مسیر درخواست |
| `service` | نام سرویس مقصد |
| `status_code` | کد وضعیت پاسخ |
| `request_time_sec` | زمان پردازش در Nginx بر حسب ثانیه |
| `user_agent` | User-Agent |

**نمونه خط لاگ:**
```json
{"timestamp":"2026-06-25T12:00:01","request_id":"req_000001","client_ip":"172.18.0.1","client_country":"Iran","scenario":"normal","method":"GET","path":"/api/teams?name=Argentina","service":"team-service","status_code":200,"request_time_sec":"0.043","user_agent":"traffic-generator"}
```

### ۷.۲. فرمت لاگ سرویس‌های backend

هر سرویس باید برای هر درخواست یک خط لاگ ساختاریافته به صورت JSON Lines بنویسد (هر خط یک JSON مستقل).

**فیلدهای مشترک و اجباری لاگ هر سرویس:**

| فیلد | توضیح |
|------|-------|
| `timestamp` | زمان رویداد (event time) |
| `request_id` | از هدر X-Request-ID (همان شناسه‌ای که از هدر می‌آید) |
| `client_country` | از هدر X-Client-Country |
| `service` | نام سرویس (مثلاً team-service) |
| `endpoint` | مسیر بدون query، مثلاً `/api/teams` |
| `entity_type` | نوع موجودیت: `team`، `match_day`، `stadium`، `city` |
| `entity_value` | مقدار موجودیت مربوط به درخواست، مثلاً `Argentina` |
| `status_code` | کد وضعیت پاسخ |
| `processing_time_ms` | زمان پردازش داخل سرویس به میلی‌ثانیه |
| `event_type` | نوع رویداد، مثلاً `team_lookup` |

سرویس باید هدرهای `X-Request-ID`، `X-Client-Country` و `X-Scenario` را که Nginx منتقل می‌کند بخواند و در لاگ خود استفاده کند.

### ۷.۳. فیلدهای هر سرویس

**match-service:**  
`entity_type` برابر `match_day` است و `entity_value` همان تاریخ درخواستی است.  
نمونه درخواست:
```
GET /api/matches?date=2026-06-25
```
خط لاگ:
```json
{"timestamp":"...","request_id":"req_000001","client_country":"Iran","service":"match-service","endpoint":"/api/matches","entity_type":"match_day","entity_value":"2026-06-25","status_code":200,"processing_time_ms":42,"event_type":"match_lookup"}
```

**team-service:**  
`entity_type` برابر `team` است و `entity_value` نام تیم است.  
نمونه درخواست:
```
GET /api/teams?name=Argentina
```
خط لاگ:
```json
{"timestamp":"...","request_id":"req_000002","client_country":"Germany","service":"team-service","endpoint":"/api/teams","entity_type":"team","entity_value":"Argentina","status_code":200,"processing_time_ms":31,"event_type":"team_lookup"}
```

**stadium-service:**  
`entity_type` برابر `stadium` یا `city` است (بسته به پارامتر).  
نمونه درخواست:
```
GET /api/stadiums?name=New York New Jersey Stadium
GET /api/stadiums?city=New York New Jersey
```

---

## ۸. پردازش با Hadoop Streaming

### ۸.۱. قرار دادن فایل ورودی روی HDFS

فایل‌های پروژه روی سیستم شما قرار دارند، اما Hadoop باید آن‌ها را از داخل محیط خود بخواند. اگر در فایل `docker-compose.yml` پروژه با volume mount پوشه‌ها را به کانتینر متصل کنید، فایل‌های محلی در مسیر `/project/data` داخل کانتینر قابل دسترسی هستند. این روش برای نگه داشتن کدها، لاگ‌ها و خروجی‌های پروژه روی سیستم میزبان مناسب است.

با این حال، برای اجرای MapReduce روی HDFS، باید فایل ورودی را با دستور `hdfs dfs -put` وارد HDFS کنید. این دستور معمولاً داخل کانتینر `namenode` اجرا می‌شود. `NameNode` مسیر فایل را مدیریت می‌کند و DataNode‌ها در نهایت فایل را ذخیره می‌کنند.

نمونه کلی:
```bash
docker compose exec namenode bash
hdfs dfs -mkdir -p /input
hdfs dfs -put -f /project/data/nginx/nginx_access.log /input/nginx_access.log
hdfs dfs -ls /input
```

اگر می‌خواهید لاگ‌های سرویس را نیز برای Job 1 وارد HDFS کنید، همین الگو را تکرار کنید:
```bash
hdfs dfs -mkdir -p /input/service_logs
hdfs dfs -put -f /project/data/service_logs/match_service.log /input/service_logs/match_service.log
hdfs dfs -put -f /project/data/service_logs/team_service.log /input/service_logs/team_service.log
hdfs dfs -put -f /project/data/service_logs/stadium_service.log /input/service_logs/stadium_service.log
hdfs dfs -ls /input/service_logs
```

> **نکته:** برای جابه‌جایی فایل بین سیستم میزبان و کانتینرها، روش اصلی `volume mount` است (پوشه‌هایی مثل `data/`، `mapreduce/`، `scripts/`، `outputs/` روی سیستم میزبان، داخل کانتینر در `/project` قابل مشاهده هستند). سپس برای اجرای واقعی روی HDFS، فایل‌های ورودی با `hdfs dfs -put` وارد HDFS می‌شوند و خروجی‌ها بعد از اجرا با `hdfs dfs -cat` یا `hdfs dfs -getmerge` به پوشه `outputs/` برگردانده می‌شوند. استفاده از `docker cp` به عنوان روش اصلی پیشنهاد نمی‌شود.

### ۸.۲. تست یک MapReduce ساده با Python

معمولاً برنامه‌های Hadoop با Java اجرا می‌شوند، اما Hadoop Streaming اجازه می‌دهد از برنامه‌های خارجی مثل اسکریپت‌های Python به عنوان mapper و reducer استفاده شوند. در این روش، Hadoop داده را از stdin به mapper می‌دهد و خروجی mapper به stdin reducer می‌رود؛ سپس reducer نیز به همین ترتیب عمل می‌کند.

برای اطمینان از اینکه محیط درست کار می‌کند، ابتدا یک تست ساده انجام دهید. فرض کنید فایل‌های زیر را در پوشه `/mapreduce/test/` نوشته‌اید.

> **نکته:** توضیحات موجود در این بخش (۸.۳) فقط جنبه آموزشی دارند و لازم نیست دانشجویان آن را اجرا کنند. هدف این است که دانشجوها با نحوه اجرای Hadoop Streaming و ساختار reducer و mapper آشنا شوند. در پروژه اصلی، دانشجوها باید mapper و reducerهای خودشان را برای تحلیل‌های مورد نیاز بنویسند.

**Mapper ساده که برای هر خط یک مقدار 1 تولید می‌کند (`mapper_line_count.py`):**

```python
#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if line:
        print("total\t1")
```

**Reducer ساده که تعداد خط‌ها را جمع می‌کند (`reducer_sum.py`):**

```python
#!/usr/bin/env python3
import sys

count = 0
for line in sys.stdin:
    key, value = line.strip().split("\t")
    count += int(value)
print("total\t%d" % count)
```

قبل از اجرای Hadoop می‌توانید همین دو فایل را به صورت محلی از داخل کانتینر تست کنید:

```bash
cd /project
cat data/nginx/nginx_access.log | python3 mapreduce/test/mapper_line_count.py | sort | python3 mapreduce/test/reducer_sum.py
```

این تست فقط برای debug است و جایگزین اجرای Hadoop Streaming نیست.

برای اجرای همین تست با Hadoop Streaming، ابتدا مطمئن شوید فایل ورودی در HDFS قرار دارد و خروجی قبلی وجود ندارد:

```bash
hdfs dfs -rm -r -f /output/test
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files mapreduce/test/mapper_line_count.py,mapreduce/test/reducer_sum.py \
    -mapper "python3 mapper_line_count.py" \
    -reducer "python3 reducer_sum.py" \
    -input /input/nginx_access.log \
    -output /output/test
```

پس از اجرا، خروجی را مشاهده کنید:
```bash
hdfs dfs -cat /output/test/part-*
```

### ۸.۳. اسکریپت اجرای کل pipeline

برای اجرای تمام Job‌ها به صورت پشت سر هم، یک اسکریپت bash بنویسید. این اسکریپت باید:

- فایل‌های ورودی را به HDFS منتقل کند (در صورت نیاز).
- Job 1 را اجرا کند.
- خروجی Job 1 را به عنوان ورودی Job 2 قرار دهد (به طریق مشابه).
- Job 2، Job 3، Job 4 و Job 5 را به ترتیب اجرا کند.
- در نهایت خروجی نهایی را در `outputs/final/summary.json` تولید کند.

نمونه بسیار ساده از ساختار یک pipeline:

```bash
#!/usr/bin/env bash
set -e
cd /project

hdfs dfs -mkdir -p /input
hdfs dfs -put -f data/nginx/nginx_access.log /input/nginx_access.log

hdfs dfs -rm -r -f /output/job1
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files mapreduce/job1_parse_clean/mapper.py,mapreduce/job1_parse_clean/reducer.py \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -input /input/nginx_access.log \
    -output /output/job1

mkdir -p outputs/job1
hdfs dfs -cat /output/job1/part-* > outputs/job1/cleaned_nginx_logs.csv

# سپس Job 2، Job 3، Job 4 و Job 5 را به همین صورت اجرا کنید.
# هر Job باید مسیر ورودی و خروجی خود را به وضوح مشخص کند.
```

در تحویل نهایی، همین اسکریپت باید همه job‌های اجباری پروژه را اجرا کند و در پایان فایل‌های خروجی مورد انتظار، مخصوصاً `outputs/final/summary.json` را بسازد.

**نتیجه مورد انتظار:**  
بعد از اجرای کامل `scripts/run_mapreduce.sh`، خروجی‌های میانی در پوشه `outputs/` و خروجی نهایی در مسیر `outputs/final/summary.json` روی سیستم میزبان قابل مشاهده باشند.

---

## ۹. MapReduce Job‌های اجباری

پردازش باید شامل پنج job اجباری باشد. این job‌ها شامل تحلیل‌های عمومی (بر اساس لاگ Nginx) و تحلیل‌های مخصوص سرویس‌ها هستند.

### Job 1: Parsing and Cleaning

**ورودی:**
- `data/nginx/nginx_access.log`
- `data/service_logs/match_service.log`
- `data/service_logs/team_service.log`
- `data/service_logs/stadium_service.log`

**وظایف:**
- خطوط نامعتبر یا ناقص را حذف کند.
- فیلدهای هر خط را استخراج و به فرمت CSV یا مناسب تبدیل کند.
- لاگ Nginx را در یک فایل خروجی (مثلاً `cleaned_nginx_logs.csv`) با فیلدهای: `timestamp`, `request_id`, `client_country`, `scenario`, `method`, `path`, `service`, `status_code`, `request_time_sec` ذخیره کند.
- لاگ‌های سرویس‌ها را به صورت یکپارچه در یک فایل (`cleaned_service_logs.csv`) با فیلدهای: `timestamp`, `request_id`, `client_country`, `service`, `endpoint`, `entity_type`, `entity_value`, `status_code`, `processing_time_ms`, `event_type` ترکیب کند.

**خروجی‌های اجباری:**
- `outputs/job1/cleaned_nginx_logs.csv`
- `outputs/job1/cleaned_service_logs.csv`

### Job 2: General Statistics (از لاگ Nginx)

**ورودی:** `cleaned_nginx_logs.csv`

**وظایف:**
- شمارش تعداد درخواست‌ها به تفکیک سرویس (`service`).
- شمارش تعداد درخواست‌ها به تفکیک endpoint (`path`).
- شمارش تعداد درخواست‌ها به تفکیک سناریو (`scenario`).

**خروجی‌های اجباری:**
- `outputs/job2/service_stats.csv`
- `outputs/job2/endpoint_stats.csv`
- `outputs/job2/scenario_stats.csv`

### Job 3: Country-Entity Request Count

این Job تحلیل‌های مخصوص سرویس‌ها را شروع می‌کند و ورودی آن `cleaned_service_logs.csv` است (لاگ سرویس‌ها، نه لاگ Nginx). هدف، شمارش تعداد درخواست‌های هر کشور برای هر موجودیت است. برای team-service، موجودیت تیم است؛ برای match-service، موجودیت تاریخ بازی است؛ برای stadium-service، موجودیت ورزشگاه یا شهر است.

نمونه مفهومی ورودی:
```
country A -> request team B
country A -> request team B
country A -> request team Z
country B -> request team Z
```

خروجی مورد انتظار برای team-service:
```
country,team,total_requests
A,B,2
A,Z,1
B,Z,1
```

**منطق کلی MapReduce:**
- Mapper: `(country, service, entity_type, entity_value) -> 1`
- Reducer: `(country, service, entity_type, entity_value) -> sum`

**خروجی‌های اجباری:**
- `outputs/job3/country_team_requests.csv`
- `outputs/job3/country_matchday_requests.csv`
- `outputs/job3/country_stadium_requests.csv`

### Job 4: Popular Entity by Country

این Job خروجی Job 3 را می‌گیرد و برای هر کشور، محبوب‌ترین موجودیت را پیدا می‌کند. به عنوان مثال، اگر خروجی Job 3 چنین باشد:

```
country,team,total_requests
Iran,Argentina,100
Iran,Brazil,80
Iran,France,30
Germany,Argentina,50
Germany,France,70
```

آن‌گاه خروجی Job 4 باید به ازای هر کشور، تیم با بیشترین درخواست را مشخص کند:

```
country,most_popular_team,total_requests
Iran,Argentina,100
Germany,France,70
```

**منطق کلی MapReduce:**
- Mapper: از هر خط، کلید `(country, entity_type)` و مقدار `(entity_value, count)` تولید شود.
- Reducer: برای هر گروه `(country, entity_type)`، موجودیت با بیشترین مجموع را پیدا کند.

**خروجی‌های اجباری (برای هر نوع موجودیت):**
- `outputs/job4/most_popular_team_by_country.csv`
- `outputs/job4/most_popular_matchday_by_country.csv`
- `outputs/job4/most_popular_stadium_by_country.csv`

### Job 5: Summary Report (Final)

این Job باید خروجی‌های Job 2، Job 3 و Job 4 را ترکیب کرده و یک فایل JSON خلاصه تولید کند. محتوای این فایل باید شامل آمارهای کلی و اطلاعات محبوب‌ترین‌ها باشد. قالب آن دلخواه است، اما باید شامل داده‌های کلیدی باشد.

**خروجی اجباری:**
- `outputs/final/summary.json`

---

## ۱۰. بخش امتیازی Spark Structured Streaming

در این بخش، دانشجوها باید با Spark Structured Streaming، لاگ‌های جدید (و در صورت نیاز لاگ‌های سرویس‌ها) را به صورت real-time بخوانند و چند خروجی زنده تولید کنند.

**حداقل خروجی‌های مورد انتظار:**
- تعداد درخواست‌ها در بازه‌های زمانی کوتاه؛
- error rate؛
- پرترافیک‌ترین سرویس یا endpoint در لحظه؛
- محبوب‌ترین تیم هر کشور در جریان داده‌های زنده؛
- میانگین response time در بازه‌های زمانی کوتاه.

خروجی real-time می‌تواند در terminal، یک فایل خروجی، یا یک صفحه ساده قابل مشاهده باشد.

### ۱۰.۱. اجرای Spark (ترجیحاً با Docker)

Spark نیز مانند Hadoop می‌تواند داخل Docker اجرا شود؛ یک ایمیج آماده از Spark (شامل PySpark) برای این کار کافی است. اجرای محلی با `spark-submit --master local[*]` نیز قابل قبول است. در حالت Docker بدون Spark، نیاز است یک نسخه پایدار از Spark 3.x اجرا کنید و برنامه را در حالت `local[*]` اجرا کنید.

> **تفاوت اصلی با بخش MapReduce:** در MapReduce پردازش به صورت batch روی کل لاگ انجام می‌شود؛ اما Spark Structured Streaming داده‌ی جدید را به صورت تدریجی و زنده پردازش می‌کند و آمارها را با رسیدن داده‌ی تازه به‌روزرسانی می‌کند.

### ۱۰.۲. Workflow پیشنهادی برای Spark

برای آمار عمومی زنده از `nginx_access.log` و برای تحلیل‌های مخصوص سرویس‌ها زنده (مثل محبوب‌ترین تیم هر کشور) از لاگ‌های سرویس‌ها استفاده کنید. ساده‌ترین روش این است که یک اسکریپت کمکی خطوط جدید لاگ را به فایل‌های کوچک تقسیم کند و داخل پوشه‌ی ورودی Spark قرار دهد. منبع تحلیل همچنان لاگ Nginx و لاگ سرویس‌هاست، نه فایل کمکی traffic generator.

> **توجه:** در Structured Streaming، خواندن از پوشه معمولاً برای فایل‌های جدید انجام می‌شود. بنابراین بهتر است برای تست، فایل‌های کوچک جدید مثل `batch_001.jsonl`، `batch_002.jsonl` ساخته شوند، نه اینکه فقط یک فایل قدیمی را بخوانید.

**ساختار پیشنهادی پوشه‌ها:**
```
data/stream/nginx/   # input files for Spark
checkpoints/spark/   # checkpoint directory
spark/streaming_app.py
```

**نمونه اجرای Spark:**
```bash
mkdir -p data/stream/nginx checkpoints/spark
spark-submit --master local[*] \
    spark/streaming_app.py \
    --input data/stream/nginx \
    --checkpoint checkpoints/spark
```

**توضیح دستور:**
- `spark-submit`: برنامه Spark را اجرا می‌کند.
- `--master local[*]`: برنامه روی همین سیستم و با همه هسته‌های موجود اجرا شود.
- `spark/streaming_app.py`: فایل اصلی برنامه Spark.
- `--input`: مسیر پوشه‌ای که Spark باید فایل‌های جدید لاگ Nginx را از آن بخواند.
- `--checkpoint`: مسیر ذخیره وضعیت stream (برای مدیریت وضعیت stream و ادامه دادن، بدون checkpoint قابل اعتماد نیست).

برای تولید ترافیک و فید کردن stream، در یک ترمینال دیگر ترافیک را از مسیر Nginx تولید کنید:

```bash
python3 traffic-generator/generate.py --nginx-url http://localhost:8080 --requests 1000
```

سپس خطوط جدید لاگ Nginx را به شکل فایل‌های کوچک وارد پوشه stream کنید. این کار می‌تواند با یک اسکریپت کمکی انجام شود، مثلاً:

```bash
python3 scripts/export_nginx_log_batches.py \
    --source data/nginx/nginx_access.log \
    --output data/stream/nginx \
    --batch-size 200
```

برای تست دستی نیز می‌توانید چند فایل کوچک ساخته شده توسط خودتان را یکی یکی وارد پوشه کنید:

```bash
cp data/manual_stream_batches/nginx_batch_001.jsonl data/stream/nginx/batch_001.jsonl
sleep 5
cp data/manual_stream_batches/nginx_batch_002.jsonl data/stream/nginx/batch_002.jsonl
```

در پیاده‌سازی بخش امتیازی، نکات کلیدی زیر را رعایت کنید: برنامه Spark باید با `readStream` از پوشه ورودی (فایل‌های JSON Lines) بخواند، در پنجره‌های زمانی کوتاه (مثلاً ۱۰ ثانیه‌ای) آمار هر سرویس را جمع بزند و خروجی زنده تولید کند. استخراج موجودیت از داده، محاسبه محبوب‌ترین تیم هر کشور و سایر خروجی‌ها بر عهده دانشجو است.

> **توجه:** در لاگ Nginx، مقدار `request_time_sec` به صورت رشته (string) ذخیره می‌شود. اگر آن را در Spark پردازش می‌کنید، حتماً نوع آن را به double cast کنید؛ در غیر این صورت ممکن است مقدار آن null شود.

برای اجرای تمیز از ابتدا، اگر می‌خواهید وضعیت قبلی stream پاک شود، پوشه checkpoint را حذف کنید:
```bash
rm -rf checkpoints/spark
```

**نتیجه مورد انتظار:**  
در بخش امتیازی، صرفاً اجرای یک کد Spark کافی نیست. باید هنگام تولید درخواست‌های جدید، خروجی زنده در terminal، فایل یا صفحه ساده دیده شود و دانشجو بتواند توضیح دهد که چگونه داده‌های جدید لاگ‌ها را خوانده و آمارها را به‌روزرسانی کرده است.

---

## ۱۱. نحوه اجرای مورد انتظار

برای اجرای سرویس‌ها و Nginx، باید بتوان از دستور زیر استفاده کرد:

```bash
docker compose up --build
```

پس از بالا آمدن سرویس‌ها، ترافیک باید با برنامه generator تولید شود. نمونه دستور:

```bash
python traffic-generator/generate.py --requests 100000 --nginx-url http://localhost:8080
```

پس از تولید ترافیک، فایل `nginx_access.log` باید شامل لاگ درخواست‌هایی باشد که از Nginx عبور کرده‌اند و فایل‌های `data/service_logs/*.log` نیز باید لاگ‌های اختصاصی سرویس‌ها را داشته باشند. سپس pipeline MapReduce مربوطه (که با `docker-compose.yml` نمونه بالا آمده است) باید از داخل محیط Hadoop اجرا شود. فایل‌های ورودی و خروجی باید از طریق مسیرهای volume mount شده در دسترس کانتینر باشند.

**نام پیشنهادی برای اسکریپت اجرا:**

```bash
bash scripts/run_mapreduce.sh
```

**نتیجه مورد انتظار:**  
در پایان اجرای فاز اول، فایل `outputs/final/summary.json` باید ساخته شده باشد و خروجی‌های میانی هر job نیز در مسیرهای مشخص شده وجود داشته باشند.

---

## ۱۲. تست دستی و مشاهده خروجی‌ها

پس از اجرای `docker compose up --build`، می‌توانید برخی از endpointها را مستقیماً در مرورگر باز کنید تا پاسخ JSON سرویس‌ها را ببینید. برای مثال، بسته به پیاده‌سازی خودتان، مسیرهایی مشابه موارد زیر باید پاسخ قابل مشاهده داشته باشند:

```
http://localhost:8080/api/teams?name=Argentina
http://localhost:8080/api/matches?date=2026-06-25
http://localhost:8080/api/stadiums?name=New+York+New+Jersey+Stadium
```

> **توجه:** تست با مرورگر فقط برای دیدن پاسخ JSON مناسب است. برای تولید لاگ کامل و معنی‌دار باید هدرهای `X-Request-ID`، `X-Client-Country` و `X-Scenario` ارسال شوند؛ مرورگر معمولی این هدرها را به راحتی اضافه نمی‌کند. برای تست اصلی از `curl` یا ابزار مشابه مانند Postman، Thunder Client استفاده کنید.

نمونه تست با `curl`:

```bash
curl -H "X-Request-ID: manual-001" \
     -H "X-Client-Country: Iran" \
     -H "X-Scenario: normal" \
     "http://localhost:8080/api/teams?name=Argentina"
```

برای مشاهده خروجی‌های نهایی در مرورگر، می‌توانید از ریشه پروژه یک HTTP server ساده اجرا کنید و فایل‌های خروجی را مشاهده نمایید.

---

**پایان فاز اول**
```