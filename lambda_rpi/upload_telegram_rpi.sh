zip -r function.zip . -x upload_telegram_rpi.sh 
aws lambda update-function-code --function-name WaterboyGetLatest --zip-file fileb://function.zip
