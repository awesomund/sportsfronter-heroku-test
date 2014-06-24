//Prod Settings
REST_API_URL = 'https://sportsfronter.iterate.no';

if (document.location.hostname === 'localhost') {
	//Test Settings
	REST_API_URL = 'http://localhost:5000'; 
} 
if (document.location.hostname === 'sportsfronter.app.iterate.no') {
	//Staging Settings
	REST_API_URL = 'https://sportsfronter.app.iterate.no';
}
