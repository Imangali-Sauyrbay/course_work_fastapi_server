import React from 'react'
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import {Link} from 'react-router-dom'


function Header() {
    return (
        <Navbar bg="light" expand="lg">
        <Container>
            <Link to={'/'} className="navbar-brand">Smartphone sell</Link>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
                <Link to={'/search'} className="nav-link">Поиск</Link>
                <Link to={'/cart'} className="nav-link">Корзина</Link>
                <Link to={'/orders'} className="nav-link">Мой заказы</Link>
                <NavDropdown title="Дополнительно" id="basic-nav-dropdown">
                    <Link to={'/addresses'} className="nav-link">Мой адреса</Link>
                    <Link to={'/bankcards'} className="nav-link">Мой банковские карты</Link>
                    <Link to={'/favs'} className="nav-link">Понравившиеся</Link>
                </NavDropdown>
            </Nav>

            <Nav className='ml-auto'>
                <Link to={'/login'} className="nav-link">Войти</Link>
                <Link to={'/reg'} className="nav-link">Создать аккаунт</Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    )
}

export default Header