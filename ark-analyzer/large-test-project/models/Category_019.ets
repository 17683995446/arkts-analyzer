export class Category_019 {

    public field0: number = 25
    public field1: number = 50
    public field2: Date = new Date()
    public field3: string = ''
    public field4: number = 63
    public field5: Date = new Date()
    public field6: Date = new Date()
    public field7: Date = new Date()
    public field8: string = 'value'
    public field9: number = 6

  constructor(data?: Partial<Category_019>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
