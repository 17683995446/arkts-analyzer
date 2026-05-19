export class Audit_145 {

    public field0: number[] = []
    public field1: Date = new Date()
    public field2: Date = new Date()
    public field3: Date = new Date()

  constructor(data?: Partial<Audit_145>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
