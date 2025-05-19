from flask import Flask
import os 
import logging
import error_code
import error_free_Code
from opencensus.ext.azure.log_exporter import AzureLogHandler


app=Flask(__name__)

INSTRMENTATION_KEY = os.environ.get("APPINSIGHTS_INSTRUMENTATIONKEY")

logger=logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

if INSTRMENTATION_KEY:
    logger.addHandler(AzureLogHandler(connection_String=f'Instrmentationkey={INSTRMENTATION_KEY}'))

def should_switch_to_goodcode():
    try:
        with open('restart.txt','r') as f:
            count=int(f.read().strip())
            return count >=1
    except:
        return False
    
def increment_restart_count():
    count=0
    try:
        with open('restart.txt','r') as f:
            count=int(f.read().strip())
    except:
        pass
    count+=1
    with open('restart.txt','w') as f:
        f.write(str(count))

@app.route('/')
def home():
    if should_switch_to_goodcode():
        import error_free_Code
        error_free_Code.run()
    else:
        try:
            import error_code
            error_code.run()
        except Exception as e:
            logger.error(f"Error occured in your code :{e}")
            increment_restart_count()
            return "Health check failed ",500
        
@app.route('/health')
def health():
    if should_switch_to_goodcode():
        return "Health code it will work",200
    else:
        try:
            import bad_code
            return "the code is not correct",200
        except Exception as e:
            logger.error("Error occured during exection : %s",traceback.format_exc())
            increment_restart_count()
            return "unhealthy - forcing restart", 500

if __name__ =='__main__':
    app.run()

    
