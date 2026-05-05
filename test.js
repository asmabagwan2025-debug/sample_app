const http = require('http');
http.get({hostname:'localhost',port:3000,path:'/'}, res => {
  console.log('statusCode', res.statusCode);
  process.exit(res.statusCode === 200 ? 0 : 1);
}).on('error', ()=> process.exit(1));
