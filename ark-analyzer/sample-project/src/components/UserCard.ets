@Component
struct UserCard {
  @Prop name: string
  @Prop email: string
  @Prop avatar: string = ''

  build() {
    Row() {
      if (this.avatar) {
        Image(this.avatar)
          .width(50)
          .height(50)
          .borderRadius(25)
      } else {
        Text(this.name.charAt(0).toUpperCase())
          .fontSize(24)
          .fontWeight(FontWeight.Bold)
          .width(50)
          .height(50)
          .backgroundColor('#7c3aed')
          .borderRadius(25)
          .textAlign(TextAlign.Center)
      }

      Column() {
        Text(this.name)
          .fontSize(18)
          .fontWeight(FontWeight.Medium)

        Text(this.email)
          .fontSize(14)
          .fontColor('#888888')
      }
      .alignItems(HorizontalAlign.Start)
      .margin({ left: 12 })
    }
    .padding(16)
    .backgroundColor('#1a1a24')
    .borderRadius(12)
  }
}

export default UserCard
