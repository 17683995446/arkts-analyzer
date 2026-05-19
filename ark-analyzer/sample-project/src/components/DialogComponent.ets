@Component
struct DialogComponent {
  @Link isVisible: boolean
  @Prop title: string
  @State content: string = ''

  build() {
    if (this.isVisible) {
      Stack() {
        Column() {
          Blank()
            .onClick(() => {
              this.isVisible = false
            })
        }
        .width('100%')
        .height('100%')
        .backgroundColor('rgba(0, 0, 0, 0.5)')

        Column() {
          Text(this.title)
            .fontSize(20)
            .fontWeight(FontWeight.Bold)
            .width('100%')
            .textAlign(TextAlign.Start)
            .padding(16)

          Divider()

          Scroll() {
            Text(this.content)
              .fontSize(14)
              .padding(16)
          }
          .layoutWeight(1)

          Divider()

          Row() {
            Button('取消')
              .onClick(() => {
                this.isVisible = false
              })
              .width('50%')

            Button('确认')
              .type(ButtonType.Primary)
              .onClick(() => {
                this.isVisible = false
              })
              .width('50%')
          }
          .height(50)
        }
        .width('80%')
        .height('60%')
        .backgroundColor('#1a1a24')
        .borderRadius(16)
      }
      .width('100%')
      .height('100%')
    }
  }
}

export default DialogComponent
