import Card from 'react-bootstrap/Card';
import Col from 'react-bootstrap/Col';
import Carousel from 'react-bootstrap/Carousel';
import Row from 'react-bootstrap/Row';

function ProductViewGrid({products}) {
    console.log(products)
    return (
        <Row xs={1} md={2} className="g-4">
            {products.map((prod) => (
            <Col>
            <Card>
                <Carousel interval={30000}>
                    {prod?.medias?.map(media => {
                        let child;

                        if (media?.content_type?.split('/')[0] === 'image') {
                            child = <img
                            className="d-block w-100"
                            src={"http://127.0.0.1:8000/media/" + media?.name}
                            alt=""
                            />
                        } else if (media?.content_type?.split('/')[0] === 'video'){
                            child = <video src={"http://127.0.0.1:8000/media/" + media?.name} controls/>
                        }


                        return (
                            <Carousel.Item>
                                {child}
                            </Carousel.Item>
                        )
                    })}
                </Carousel>
                <Card.Body>
                <Card.Title>{ prod.title }</Card.Title>
                <Card.Text>
                    {prod.description}
                </Card.Text>
                <Card.Footer>
                    {prod?.sellers.map(seller => {
                        return (
                            <div>
                                <span>{seller?.address?.city} </span>
                                <span>{seller?.local_price} </span>
                                <span>{seller?.local_currency} </span>
                                <br />
                                <span>В Складе: {seller?.quantity} </span>
                                <span>Продовец: {seller?.seller?.name} </span>
                                <hr />
                            </div>
                        )
                    })}
                </Card.Footer>
                </Card.Body>
            </Card>
            </Col>
        ))}
        </Row>
    )
}

export default ProductViewGrid