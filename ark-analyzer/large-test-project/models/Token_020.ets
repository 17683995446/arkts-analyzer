export class Follow_020 {

    public field0: number[] = []
    public field1: Date = new Date()
    public field2: boolean = false
    public field3: number[] = []

  constructor(data?: Partial<Follow_020>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
