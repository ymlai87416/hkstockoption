import summary_config

print(summary_config.stock_spreadsheet_id)

# a = append and w = write
f = open("/app/service_account.json", "r", encoding='UTF-8')

# read
print(f.readline())
f.close()