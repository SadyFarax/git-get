<div dir="rtl" align="right">
🧨 دانلودر گیت گت
یک اسکریپت تخمی، برای شرایط تخمی تر ، که توی گیتهاب اکشنز کار می‌کنه و همه چی رو با یه خط کامند می‌گیره.
فقط کافیه توی فیلد اجرا بنویسی کامندتو، هر خط یه کامند. آخرش ZIP تحویلت میده.

🔧 کامندای قابل قبول
wget برای دانلود مستقیم یه فایل
wget <لینک> [o=نام_خروجی]
مثال:
wget https://example.com/file.zip o=myfile.zip

git برای کلون کردن یه مخزن Git (مثل مدلای HuggingFace با LFS)
git <آدرس_مخزن> [b=شاخه] [d=پوشه] [lfs=true] [depth=1]
مثال:
git https://huggingface.co/bert-base-uncased b=main d=bert lfs=true

mirror برای آینه کردن کامل یه وبسایت
mirror <آدرس_سایت> [o=پوشه] [depth=1000]
مثال:
mirror https://example-docs.com o=docmirror depth=500

روش استفاده :

توی تب Actions، روی Multi Downloader کلیک کن، Run workflow رو بزن

توی باکس بزرگ کامندات رو بنویس

اسم ZIP خروجی رو هم می‌تونی عوض کنی

دکمهٔ سبز رو بزن تا اجرا بشه

بعد از اتمام، از Artifacts فایل ZIP رو بردار.
.

</div>
