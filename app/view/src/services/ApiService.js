

class ApiService {
    constructor(baseUrl = '/api/') {
        this.baseUrl = baseUrl
    }

    getConfig(headers={}) {
        return {
            headers: {
                'accept': 'application/json',
                ...headers
            },
            method: 'GET'
        }
    }

    postConfig(body = {}, headers = {}, method = 'POST') {
        return {
            headers: {
                'accept': 'application/json',
                ...headers
            },
            method,
            body: body instanceof FormData ? body : JSON.stringify(body)
        }
    }

    async getCategories() {
        const res = await fetch(this.baseUrl + 'categories', this.getConfig())
        return await res.json()
    }

    async getProductAddresses() {
        const res = await fetch(this.baseUrl + 'products/addresses', this.getConfig())
        return await res.json()
    }

    async getOrderableColumns() {
        const res = await fetch(this.baseUrl + 'products/orderable', this.getConfig())
        return await res.json()
    }

    async getProducts({
        query_text=null,
        category_id=0,
        order_by_column='id',
        order_by='ASC',
        min_price=null,
        max_price=null,
        currency='USD',
        page=1,
        per_page=10,
        city=null,
        country=null
    } = {}) {
        const params = {
            query_text, category_id, order_by_column,
            order_by, min_price, max_price, currency,
            page, per_page, city, country
        }
        const url = new URLSearchParams(Object.entries(params).filter(([,val]) => !!val)).toString()
        const res = await fetch(this.baseUrl + 'products?' + url, this.getConfig())
        return await res.json()
    }

    async getProduct({
        product_id=0,
        currency='USD',
    } = {}) {
        const params = {
            currency
        }
        const url = new URLSearchParams(Object.entries(params).filter(([,val]) => !!val)).toString()
        const res = await fetch(this.baseUrl + 'products/' +  product_id + '?' + url, this.getConfig())
        return await res.json()
    }

    async createProduct({
        title,
        description,
        characteristics,
        category_id,
        price,
        quantity,
        address_id,
        bank_card_id,
        token="",
        currency='USD',
        media=[]
    } = {}) {
        const form = new FormData()
        form.append('media[]', media)
        
        const params = {
            title,
            description,
            characteristics,
            category_id,
            price,
            quantity,
            address_id,
            bank_card_id,
            currency,
        }

        const url = new URLSearchParams(Object.entries(params).filter(([,val]) => !!val)).toString()
        const res = await fetch(this.baseUrl + 'products?' + url, this.postConfig(form, {"Contetnt-Type": "multipart/form-data", "x-token": token}))
        return await res.json()
    }

    async putProductSeller({
        product_id,
        address_id,
        bank_card_id,
        price,
        quantity,
        currency='USD',
        token 
    } = {}) {
        const params = {
            address_id,
            bank_card_id,
            price,
            quantity,
            currency,
        }

        const url = new URLSearchParams(Object.entries(params).filter(([,val]) => !!val)).toString()
        const res = await fetch(this.baseUrl + 'products/' + product_id + '/seller?' + url, this.postConfig({}, {"x-token": token}, 'PUT'))
        return await res.json()
    }

    async deleteProductSeller({
        product_seller_id,
        token 
    } = {}) {
        const params = {
            product_seller_id
        }

        const url = new URLSearchParams(Object.entries(params).filter(([,val]) => !!val)).toString()
        const res = await fetch(this.baseUrl + 'products/seller?' + url, this.postConfig({}, {"x-token": token}, 'DELETE'))
        return await res.json()
    }

    async likePost({
        liked,
        product_id,
        token
    }) {
        const params = {
            liked,
            product_id
        }

        const url = new URLSearchParams(Object.entries(params).filter(([,val]) => !!val)).toString()
        const res = await fetch(this.baseUrl + 'like?' + url, this.postConfig({}, {"x-token": token}))
        return await res.json()
    }

    async getUser(token) {
        const res = await fetch(this.baseUrl + 'user', this.getConfig({"x-token": token}))
        return await res.json()
    }

    async login(email, password) {
        const url = new URLSearchParams([['email', email], ['password', password]]).toString()
        const res = await fetch(this.baseUrl + 'login?' + url, this.postConfig())
        return await res.json()
    }

    async register({name, email, password, role} = {}) {
        const params = {name, email, password, role}
        const url = new URLSearchParams(Object.entries(params)).toString()
        const res = await fetch(this.baseUrl + 'reg?' + url, this.postConfig())
        return await res.json()
    }

    async getRoles() {
        const res = await fetch(this.baseUrl + 'roles', this.getConfig())
        return await res.json()
    }

    async getBankCards(token="") {
        const res = await fetch(this.baseUrl + 'bankcards', this.getConfig({'x-token': token}))
        return await res.json()
    }

    async createBankCard({
        token="",
        holder,
        number,
        expires,
        cvv
    }) {
        const params = {holder, expires, number, cvv}
        const url = new URLSearchParams(Object.entries(params)).toString()
        const res = await fetch(this.baseUrl + 'bankcards?' + url, this.postConfig({}, {'x-token': token}))
        return await res.json()
    }

    async updateBankCard({
        token="",
        bank_card_id,
        holder = null,
        number = null,
        expires = null,
        cvv = null
    }) {
        const params = {holder, expires, number, cvv, bank_card_id}
        const url = new URLSearchParams(Object.entries(params).filter(([,val]) => !!val)).toString()
        const res = await fetch(this.baseUrl + 'bankcards?' + url, this.postConfig({}, {'x-token': token}), 'PUT')
        return await res.json()
    }

    async deleteBankCard({
        token="",
        bank_card_id,
    }) {
        const params = {bank_card_id}
        const url = new URLSearchParams(Object.entries(params)).toString()
        const res = await fetch(this.baseUrl + 'bankcards?' + url, this.postConfig({}, {'x-token': token}), 'DELETE')
        return await res.json()
    }

    async getAddresses(token="") {
        const res = await fetch(this.baseUrl + 'address', this.getConfig({'x-token': token}))
        return await res.json()
    }

    async createAddress({
        token="",
        country,
        city,
        street,
        house,
        postal_code
    }) {
        const params = {country, city, street, house, postal_code}
        const url = new URLSearchParams(Object.entries(params)).toString()
        const res = await fetch(this.baseUrl + 'address?' + url, this.postConfig({}, {'x-token': token}))
        return await res.json()
    }

    async updateAddress({
        token="",
        address_id,
        country = null,
        city = null,
        street = null,
        house = null,
        postal_code = null
    }) {
        const params = {country, city, street, house, postal_code, address_id}
        const url = new URLSearchParams(Object.entries(params).filter(([,val]) => !!val)).toString()
        const res = await fetch(this.baseUrl + 'address?' + url, this.postConfig({}, {'x-token': token}), 'PUT')
        return await res.json()
    }

    async deleteAddress({
        token="",
        address_id,
    }) {
        const params = {address_id}
        const url = new URLSearchParams(Object.entries(params)).toString()
        const res = await fetch(this.baseUrl + 'address?' + url, this.postConfig({}, {'x-token': token}), 'DELETE')
        return await res.json()
    }
}

const api = new ApiService()
export {api, ApiService}