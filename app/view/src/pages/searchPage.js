import SearchForm from "../components/searchForm"
import ProductViewGrid from "../components/productViewGrid"
import { NotificationManager } from 'react-notifications';
import {api} from '../services/ApiService'
import { useState } from "react";

function SearchPage() {

    const [products, setProducts] = useState({})

    function handler(data) {
        api.getProducts(data)
        .then(res => setProducts(res))
        .catch(e => NotificationManager.error('Ошибка загрузки', 'Попробуйте перезагрузить страницу!', 4000))
    }

    return (
        <> 
            <SearchForm showData={handler}/>
            <ProductViewGrid products={products.items || []}/>
        </>
    )
}

export default SearchPage