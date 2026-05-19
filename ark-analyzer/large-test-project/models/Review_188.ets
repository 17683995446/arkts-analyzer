export class Audit_188 {

    public field0: string[] = []
    public field1: boolean = false
    public field2: Date = new Date()

  constructor(data?: Partial<Audit_188>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
