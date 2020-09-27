# General overview

## Base response structure

Server response has next general structure:

```
{
  "ok": <bool:>,
  "data": <object:>,
  "status": {
    "datetime": <datetime:>,
    "message": <str:>
  }
}
```
- `ok` is a variable that carries server status of response:
    - if `true` than no errors were arisen.
    - if `false` than server recieved some request mistakes.
- `data` is a json object which provides requested data if it is providable.
- `status` is a json object which provides two server response status variables:
    - `timestamp` is a time of response.
    - `message` is a message of error or success response.


## List of Errors

| Error message | Server Error Code | Recieved if |
| ----------- | ----------- | ----------- |
| *Authorization failed* | 400 | User with sended credentials which isn't in a database.|
| *Wrong types* | 400 | Any parameter in json body has wrong data type. |
| *No request body* | 400 | There is no json body in a request. |
| *Not an authorized request* | 401 | A request provided no `Authorization` header or token from header isn't authenicated on api service. |
| *Not found* | 404 | Query to database returned `NoneType` |
| *Missing parameters* | 406 | Not all required parameters are provided. |
| *Is already in database* | 409 | Query to database was not validated because non-unique parameters. |
| *Already authorized* | 423 | Server gets request with `Authorization` header when it is disallowed.|

# Endpoints

## Endpoints related to `/user` route

### `POST /user` - gets user data by id.

Request format:
```
# Returns user data by id

POST /user
Authorization: <str:token>

{
    "id": <int:> # Optional parameter
}

#OR
#Returns current user data

POST /user
Authorization: <str:token>

{} # Optional json body
```

Response if ok:
```
{
  'ok': True,
  'data': {
    'user': {
      'id': <int:>,
      'username': <str:>,
      'status': <str:>,
      'nickname': <str:>,
      'avatar':  <str:>,
      'email':  <str:>
    }
  },
  'status': {
    'datetime': <datetime:>,
    'message': "User queried"
  }
}
```
Possible errors:
- *`Wrong types`*
- *`Not found`*
- *`Not an authorized request`*
- *`No request body`*

### `POST /user/login` - authorizes user to api.

Request format:
```
POST /user/login
Authorization: <str:token>

{
  "username": <str:>,
  "password": <str:>
}
```

Response if ok:
```
{
  "ok": true,
  "data": {
    "token": <str:>
  },
  "status": {
    "datetime": <datetime:>,
    "message": "Authorized"
  }
}
```
Possible errors:
- *`Already authorized`*
- *`Authorization failed`*
- *`Missing parameters`*

### `POST /user/logout` - deauthorizes user.

Request formats:
```
POST /user/logout
Authorization: <str:token>

{} # json body is optional
```

Response if ok:
```
{
  "ok": true,
  "data": {},
  "status": {
    "datetime": <datetime:>,
    "message": "Deauthorized"
  }
}
```
Possible errors:
- *`Not an authorized request`*

### `POST /user/add-user` - adds user to db.

Request formats:
```
POST /user/add-user
Authorization: <str:token>

{
  'username': <str:>
  'password': <str:>
  'nickname': <str:> # optional field
  'email': <str:>
  'avatar': <str:>  # optional field
}
```

Response if ok:
```
{
  "ok": true,
  "data": {},
  "status": {
    "datetime": <datetime:>,
    'message': "Created user with <int:id>"
  }
}
```
Possible errors:
- *`Missing parameters`*
- *`Is already in database`*
- *`No request body`*

### `POST /user/del-user` - removes user from db.

Request formats:
```
POST /user/del-user
Authorization: <str:token>

{} # json body is optional
```

Response if ok:
```
{
  "ok": true,
  "data": {},
  "status": {
    "datetime": <datetime:>,
    'message': "Created user with <int:id>"
  }
}
```
Possible errors:
- *`Not an authorized request`*