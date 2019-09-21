zip -r function.zip . -x upload_telegram_update.sh 
aws lambda update-function-code --function-name TelegramWaterboyUpdate --zip-file fileb://function.zip
