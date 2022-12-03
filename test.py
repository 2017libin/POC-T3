import shodan
SHODAN_API_KEY = "3p8GQqpTsiyx84KgKnnH8asN46Qqb8zO"
api = shodan.Shodan(SHODAN_API_KEY)
try:
    results = api.search('Apache')
    print ('Results found: %s' % results['total'])
    for index, result in enumerate( results['matches']):         
            print ("%s: %s:%s|%s|%s"%(index,result['ip_str'],result['port'],result['location']['country_name'],result['hostnames']))
except shodan.APIError as e:
    print ('Error: %s' % e)