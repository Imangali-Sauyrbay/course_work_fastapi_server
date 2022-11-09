import React, {useState, useEffect} from 'react';
import {Container} from 'react-bootstrap'
import { Route, Routes } from 'react-router-dom';
import './App.css';
import {api} from './services/ApiService'
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-notifications/lib/notifications.css';
import { NotificationContainer } from 'react-notifications';
import Header from './components/header'
import MainPage from './pages/mainPage'
import SearchPage from './pages/searchPage'
import {userContext} from './contexts/userContext'

function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {}, [])

  return (
    <userContext.Provider value={{ user: user }}>
      <Header/>
      <Container>
        <Routes>
          <Route path='/' element={<MainPage />}/>
          <Route path='/search' element={<SearchPage />}/>
        </Routes>
      </Container>
      <NotificationContainer />
    </userContext.Provider>
  );
}

export default App;
