@Entry
@Component
struct Page_072 {
  @State pageTitle: string = 'Page 72'
  @State loading: boolean = false
  @State data: string[] = []
  
  aboutToAppear() {
    this.loadData()
  }
  
  build() {
    Column() {
      Text(this.pageTitle)
        .fontSize(28)
        .fontWeight(FontWeight.Bold)
        .margin({ bottom: 20 })
      
      if (this.loading) {
        LoadingProgress()
          .width(50)
          .height(50)
      } else {
        List() {
          ForEach(this.data, (item: string) => {
            ListItem() {
              Text(item)
                .fontSize(16)
                .padding(10)
            }
          })
        }
        .width('100%')
        .height(300)
      }
      
      Button('Refresh')
        .margin({ top: 20 })
        .onClick(() => {
          this.loadData()
        })
    }
    .width('100%')
    .padding(20)
  }
  
  async loadData() {
    this.loading = true
    await this.simulateApiCall()
    this.data = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
    this.loading = false
  }
  
  simulateApiCall(): Promise<void> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve()
      }, 500)
    })
  }
}
