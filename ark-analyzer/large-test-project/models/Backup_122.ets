export class Product_122 {

    public field0: boolean = true
    public field1: number[] = []
    public field2: boolean = false
    public field3: string[] = []
    public field4: string[] = []
    public field5: number = 96
    public field6: string[] = []
    public field7: string[] = []
    public field8: string[] = []
    public field9: boolean = true

  constructor(data?: Partial<Product_122>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
