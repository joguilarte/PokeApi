# PokeApi
API para interactuar con "https://pokeapi.co/api/v2/"

PokeApi es una API desarrollada en Python utilizando el framework 
Flask que permite obtener información sobre los Pokémon. La API 
cuenta con un esquema de autenticación y autorización para 
garantizar la seguridad de los datos.


Para probar la API, puedes descargar la imagen Dockerizada desde 
Docker Hub utilizando el comando docker pull jguilartegg/poke_apiv3. Luego, 
puedes ejecutar la imagen utilizando el comando docker run -p 5000:5000 
jguilartegg/poke_apiv3 para iniciar la aplicación en el puerto 5000.
Una vez que la aplicación esté en ejecución, puedes interactuar con la 
API utilizando una herramienta como Postman. Para hacerlo, debes 
enviar solicitudes HTTP a los diferentes endpoints de la API, 
especificando el método HTTP adecuado (GET, POST, DELETE, etc.) 
y proporcionando los datos necesarios en el cuerpo de la solicitud o en 
los parámetros de la URL.

El usuario admin: 

user: admin
pass: pass

Para usar los endpoints de la API con Postman, debes seguir estos 
pasos:
1. Abre Postman y crea una nueva solicitud.
2. Selecciona el método HTTP adecuado (GET, POST, DELETE, 
etc.) según el endpoint que deseas utilizar.
3. Ingresa la URL del endpoint en el campo “Enter request URL”, 
reemplazando <host> con la dirección IP o el nombre de host 
donde se está ejecutando la aplicación y <port> con el puerto 
donde se está ejecutando (por defecto es 5000). Por ejemplo, si 
estás ejecutando la aplicación en tu computadora local, puedes 
ingresar http://localhost:5000/login para utilizar el endpoint de inicio de 
sesión.
4. Si el endpoint requiere datos en el cuerpo de la solicitud (por 
ejemplo, el endpoint de inicio de sesión requiere un username y un 
password), selecciona la pestaña “Body” y luego selecciona “raw” y 
“JSON” en las opciones desplegables. Luego, ingresa los datos 
necesarios en formato JSON en el campo de texto.
5. Si el endpoint requiere un token de acceso JWT (todos los 
endpoints excepto register), selecciona la pestaña 
“Headers” y agrega un nuevo encabezado con el nombre 
“Authorization” y el valor “Bearer <token>”, reemplazando <token>
con el token de acceso obtenido al iniciar sesión.
6. Haz clic en el botón “Send” para enviar la solicitud a la API. Los 
resultados se mostrarán en la sección “Response”.
