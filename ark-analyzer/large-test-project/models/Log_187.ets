export class Product_187 {

    public field0: number[] = []
    public field1: string[] = []
    public field2: string = 'value'

  constructor(data?: Partial<Product_187>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
