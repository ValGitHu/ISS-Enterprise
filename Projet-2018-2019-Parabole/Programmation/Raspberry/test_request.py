import requests
r = requests.get('https://www.google.com/search?q=url+google')
a = r.status_code
print(r)
if(a == 200):
  print ("connexion reussis")
if(a == 404):
  print ("page non trouvée")
