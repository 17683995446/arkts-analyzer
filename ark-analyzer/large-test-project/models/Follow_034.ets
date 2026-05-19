export class Notification_034 {

    public field0: string[] = []
    public field1: string = 'default'
    public field2: Date = new Date()
    public field3: number = 83
    public field4: Date = new Date()
    public field5: string[] = []
    public field6: string = 'test'
    public field7: number = 76
    public field8: number[] = []
    public field9: number[] = []
    public field10: number = 37
    public field11: Date = new Date()

  constructor(data?: Partial<Notification_034>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
