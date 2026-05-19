export class Category_131 {

    public field0: string[] = []
    public field1: number[] = []
    public field2: string[] = []
    public field3: string[] = []
    public field4: string[] = []
    public field5: Date = new Date()
    public field6: string[] = []
    public field7: string[] = []
    public field8: number = 31

  constructor(data?: Partial<Category_131>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
