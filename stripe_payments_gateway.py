import os
import dotenv
import stripe
import stripe.error

# Configuración del entorno
dotenv.load_dotenv()
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

# configurando para poder conectarnos a nuestra pasarela de pago de Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Crear método de pago
# simulación de que al usuario le salga una ventana para que meta los datos el usuario como el CVV, etc
# cards de prueba: https://docs.stripe.com/testing
def create_payment_method() -> str:

    try:
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={"token": "tok_visa"}
        )

        print(f"Método de pago creado: {payment_method.id}")

        return payment_method.id
    except stripe.error.StripeError as e:
        print(f"Error en Stripe: {e.user_message}")

# Crear un pago
def create_payment(client_id: str, payment_method_id: str, product_id: str, amount: int, currency: str):

    try:
        # intención de pago, que necesito para crear un pago
        payment = stripe.PaymentIntent.create(
            amount=amount, # trabajamos con céntimos
            currency=currency,
            customer=client_id,
            payment_method =payment_method_id,
            payment_method_types=["card"],
            confirm=True, # confirmar pago por parte del usuario
            metadata={
                "product_id" : product_id
            }
        )

        print(f"Pago con ID {payment.id} realizado correctamente")

    except stripe.error.CardError as e:
        print(f"Error en la tarjeta: {e.user_message}")
    except stripe.error.StripeError as e:
        print(f"Error en Stripe: {e.user_message}")

# crear un cliente
def create_user(name: str, email: str): 

    try:
        client = stripe.Customer.create(
            name=name,
            email=email
        )

        print(f"Cliente {name} creado con ID: {client.id}")

        return client.id
    
    except stripe.error.StripeError as e:
        print(f"Error en Stripe: {e.user_message}")


# Asociar método de pago a usuario
def add_payment_method_to_user(client_id: str, payment_method_id: str):
    try:
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=client_id
        )

        print(f"Método de pago {payment_method_id} asociado a cliente {client_id}")
    except stripe.error.StripeError as e:
        print(f"Error en Stripe: {e.user_message}")


# obtener productos
def get_products() -> str:
    try:
        products = stripe.Product.list(limit=1)
        #for product in products:
        #    print(f"Producto: {product}")

        return products["data"][0]["id"]
    
    except stripe.error.StripeError as e:
        print(f"Error en Stripe: {e.user_message}")

def get_product_price(product_id: str):
    price = stripe.Price.list(product=product_id, limit=1)
    
    price_id = price["data"][0]["id"]
    amount = price["data"][0]["unit_amount"]
    currency = price["data"][0]["currency"]
    #print(price)

    return price_id, amount, currency

# Prueba
client_id = create_user("Jordi", "jordi@test.com")

payment_method_id = create_payment_method()

add_payment_method_to_user(client_id, payment_method_id)

product_id = get_products()
price_id, amount, currency = get_product_price(product_id)

create_payment(client_id, payment_method_id, product_id, amount, currency)