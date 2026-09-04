export interface CartProduct {
  id: number
  slug: string
  title: string
  price: number
  image?: string | null
}

export interface CartItem {
  product: CartProduct
  quantity: number
}