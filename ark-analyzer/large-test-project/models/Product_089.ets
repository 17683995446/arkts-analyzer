export class Notification_089 {

    public field0: Date = new Date()
    public field1: string[] = []
    public field2: boolean = false
    public field3: string[] = []
    public field4: number = 6

  constructor(data?: Partial<Notification_089>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
