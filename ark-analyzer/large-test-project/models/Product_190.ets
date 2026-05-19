export class Token_190 {

    public field0: number[] = []
    public field1: string = 'test'
    public field2: number[] = []

  constructor(data?: Partial<Token_190>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
