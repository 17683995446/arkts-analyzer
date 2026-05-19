export class Backup_081 {

    public field0: number[] = []
    public field1: number = 90
    public field2: Date = new Date()
    public field3: string[] = []
    public field4: boolean = true
    public field5: string[] = []
    public field6: number = 31
    public field7: number[] = []

  constructor(data?: Partial<Backup_081>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
