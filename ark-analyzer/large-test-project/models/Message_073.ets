export class Category_073 {

    public field0: string[] = []
    public field1: number[] = []
    public field2: string[] = []
    public field3: string = 'test'
    public field4: boolean = false
    public field5: Date = new Date()

  constructor(data?: Partial<Category_073>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
