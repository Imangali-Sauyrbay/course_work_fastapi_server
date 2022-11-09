import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import InputGroup from 'react-bootstrap/InputGroup';
import Accordion from 'react-bootstrap/Accordion';
import { NotificationManager } from 'react-notifications';
import { useEffect, useState } from 'react'
import {api} from '../services/ApiService'


function SearchForm({showData}) {
    const [categories, setCategories] = useState([])
    const [orderables, setOrderables] = useState([])
    const [addresses, setAddresses] = useState({})

    const [minPrice, setMinPrice] = useState(null)
    const [maxPrice, setMaxPrice] = useState(null)
    const [orderCol, setOrderCol] = useState(null)
    const [orderBy, setOrderBy] = useState('ASC')
    const [category, setCategory] = useState(0)
    const [text, setText] = useState('')
    const [city, setCity] = useState(null)
    const [country, setCountry] = useState(null)
    const [curency, setCurency] = useState('KZT')


    useEffect(() => {
        api.getCategories()
        .then((res) => setCategories(res))
        .catch(err => NotificationManager.error('Ошибка загрузки категорий', 'Попробуйте перезагрузить страницу!', 4000))

        api.getOrderableColumns()
        .then((res) => setOrderables(res))
        .catch(err => NotificationManager.error('Ошибка загрузки колонок', 'Попробуйте перезагрузить страницу!', 4000))
    
        api.getProductAddresses()
        .then((res) => setAddresses(res))
        .catch(err => NotificationManager.error('Ошибка загрузки адрессов', 'Попробуйте перезагрузить страницу!', 4000))

    
    }, [])

    return (
        <Form className="mb-5">
            <Form.Group className="mb-3">
                <Form.Label>Поиск:</Form.Label>
                <Form.Control type="text" placeholder="Поиск" value={text} onInput={e => setText(e.target.value)}/>
            </Form.Group>


            <Accordion className={'mb-3'}>
                <Accordion.Item eventKey="0">
                    <Accordion.Header>Расширенные настройки</Accordion.Header>
                    <Accordion.Body>
                        <Form.Select aria-label="Выберите категорию" className="mb-3" onInput={e => setCategory(+e.target.value)}>
                            <option disabled>Выберите категорию</option>
                            <option value={0}>Все категорий</option>
                            { categories.map(ctg => <option key={ctg.id} value={ctg.id}>{ctg.name}</option>) }
                        </Form.Select>

                        <InputGroup>
                            <Form.Select aria-label="Сортировать по" className="mb-3" onInput={e => setOrderCol(e.target.value)}>
                                <option value={''}>Выберите колонку для сортировки</option>
                                { orderables.map(ord => <option key={ord.value} value={ord.value}>{ord.alias}</option>) }
                            </Form.Select>

                            <Form.Select aria-label="Сортировка по" className="mb-3" onInput={e => setOrderBy(e.target.value)}>
                                <option disabled>Сортировка по</option>
                                <option value={'ASC'}>Возрастанию</option>
                                <option value={'DESC'}>Убыванию</option>
                            </Form.Select>
                        </InputGroup>
                    
                        <InputGroup className='d-flex justify-content-around'>
                            <Form.Group className="mb-3">
                                <Form.Label>Минимальная цена:</Form.Label>
                                <Form.Control type="number" placeholder="Min." onInput={e => setMinPrice(e.target.value)}/>
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Максимальная цена:</Form.Label>
                                <Form.Control type="number" placeholder="Max." onInput={e => setMaxPrice(e.target.value)}/>
                            </Form.Group>
                        </InputGroup>

                        <InputGroup>
                            <Form.Select aria-label="Выберите страну" className="mb-3" onInput={e => setCountry(e.target.value)}>
                                <option value={''}>Выберите страну</option>
                                { addresses?.countries?.map(cntry => <option key={cntry} value={cntry}>{cntry}</option>) }
                            </Form.Select>

                            <Form.Select aria-label="Выберите город" className="mb-3" onInput={e => setCity(e.target.value)}>
                                <option value={''}>Выберите город</option>
                                { addresses?.cities?.map(city => <option key={city} value={city}>{city}</option>) }
                            </Form.Select>

                        </InputGroup>

                        <Form.Select aria-label="Выберите валюту" className="mb-3" onInput={e => setCurency(e.target.value)}>
                                <option disabled>Выберите валюту</option>
                                <option value={'KZT'}>Тенге</option>
                                <option value={'RUB'}>Рубль</option>
                                <option value={'EUR'}>Евро</option>
                                <option value={'USD'}>Доллары США</option>
                        </Form.Select>
                    </Accordion.Body>
                </Accordion.Item>
            </Accordion>
            

            <InputGroup className='d-flex justify-content-center'>
                <Button variant="primary" type="submit" onClick={e => {
                    e.preventDefault()
                    showData({
                        query_text: text,
                        category_id: category,
                        order_by_column: orderCol,
                        order_by: orderBy,
                        min_price: minPrice,
                        max_price: maxPrice,
                        currency: curency,
                        page: 1,
                        per_page: 100,
                        city,
                        country
                    })
                }}>
                    Submit
                </Button>
            </InputGroup>
      </Form>
    )
}

export default SearchForm