# Product Specifications

## E-Shop Checkout System

### Product Catalog

#### 1. Wireless Headphones
- **Product ID**: 1
- **Name**: Wireless Headphones
- **Price**: $79.99
- **Description**: High-quality wireless headphones with noise cancellation
- **Stock**: Available
- **Category**: Electronics

#### 2. Smart Watch
- **Product ID**: 2
- **Name**: Smart Watch
- **Price**: $199.99
- **Description**: Advanced fitness tracking and notifications
- **Stock**: Available
- **Category**: Wearables

#### 3. Laptop Stand
- **Product ID**: 3
- **Name**: Laptop Stand
- **Price**: $49.99
- **Description**: Ergonomic adjustable laptop stand
- **Stock**: Available
- **Category**: Accessories

### Discount Codes

The checkout system supports promotional discount codes. Valid codes include:

#### SAVE15
- **Type**: Percentage discount
- **Value**: 15% off entire order
- **Valid for**: All products
- **Minimum order**: None
- **Expiration**: None
- **Usage**: Case-insensitive

#### SAVE20
- **Type**: Percentage discount
- **Value**: 20% off entire order
- **Valid for**: All products
- **Minimum order**: $100
- **Expiration**: None
- **Usage**: Case-insensitive

#### FREESHIP
- **Type**: Free shipping
- **Value**: Waives express shipping fee
- **Valid for**: Express shipping only
- **Minimum order**: None
- **Expiration**: None
- **Usage**: Case-insensitive

### Discount Code Rules
- Codes are case-insensitive (SAVE15 = save15 = Save15)
- Applied before tax calculation
- Only one discount code per order
- Invalid codes display: "Invalid promo code. Please try again."
- Empty code submission displays: "Please enter a promo code"
- Successfully applied codes show: "Promo code [CODE] applied successfully!"

### Shipping Methods

#### Standard Shipping
- **Cost**: Free ($0.00)
- **Delivery time**: 5-7 business days
- **Tracking**: Provided
- **Default**: Yes

#### Express Shipping
- **Cost**: $10.00
- **Delivery time**: 1-2 business days
- **Tracking**: Provided with real-time updates
- **Default**: No

### Payment Methods

#### Credit Card
- **Supported cards**: Visa, MasterCard, American Express, Discover
- **Processing**: Secure payment gateway
- **Default**: Yes

#### PayPal
- **Processing**: Redirects to PayPal
- **Requirements**: Valid PayPal account
- **Default**: No

### Order Calculation

1. **Subtotal**: Sum of all items (quantity × price)
2. **Discount**: Applied to subtotal (percentage-based)
3. **Shipping**: Added after discount
4. **Total**: Subtotal - Discount + Shipping

### Form Validation Rules

#### Full Name
- **Required**: Yes
- **Format**: Text string
- **Min length**: 2 characters
- **Error message**: "Please enter your full name"

#### Email Address
- **Required**: Yes
- **Format**: Valid email (contains @ and domain)
- **Validation**: HTML5 email validation
- **Error message**: "Please enter a valid email address"

#### Phone Number
- **Required**: Yes
- **Format**: Numbers, spaces, hyphens, parentheses, plus sign
- **Pattern**: [0-9\-\+\s\(\)]+
- **Error message**: "Please enter a valid phone number"

#### Shipping Address
- **Required**: Yes
- **Format**: Multiline text
- **Min length**: 10 characters
- **Error message**: "Please enter your shipping address"

### Cart Functionality

#### Add to Cart
- Clicking "Add to Cart" adds one unit to cart
- If item already in cart, increments quantity
- Cart updates automatically

#### Update Quantity
- Users can change quantity using number input
- Minimum quantity: 1
- Setting to 0 removes item from cart
- Prices update automatically

#### Remove from Cart
- Click the "✕" button to remove item
- Cart recalculates automatically
- If cart empty, shows "Your cart is empty"

### Checkout Process

1. User adds products to cart
2. User optionally applies promo code
3. User fills in personal details
4. User selects shipping method
5. User selects payment method
6. User clicks "Pay Now"
7. Form validates all fields
8. If valid, displays "Payment Successful!" message
9. Form is hidden on success

### Error Handling

- Empty cart on checkout: "Your cart is empty. Please add items before checkout."
- Invalid form fields: Individual field error messages in red
- Invalid promo code: "Invalid promo code. Please try again."
- Form submission with errors: Prevents submission and shows validation messages
