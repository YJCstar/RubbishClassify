import torch
import torchvision
import torch.nn as nn
from DataLodaer import train_data, test_data

# 数据加载
train_loader = DataLoader(dataset=train_data, batch_size=30, shuffle=True)
test_loader = DataLoader(dataset=test_data, batch_size=30)

# GPU训练
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(device)

# 初始化模型
pretrained_net = torchvision.models.googlenet(pretrained=True)
pretrained_net.fc = nn.Linear(1024, 40)
print('模型加载完毕')

# 微调模型
output_params = list(map(id, pretrained_net.fc.parameters()))
feature_params = filter(lambda p: id(p) not in output_params, pretrained_net.parameters())

model = pretrained_net
model.to(device)

num_epochs = 20
Loss_list = []
total_step = len(train_loader)

lr = 0.01
criterion = nn.CrossEntropyLoss()  # 交叉熵损失函数
optimizer = torch.optim.SGD([{'params': feature_params},
                             {'params': pretrained_net.fc.parameters(), 'lr': lr * 10}],
                            lr=lr, weight_decay=0.001)

print('开始训练')
model.train()
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        images = images.to(device)
        labels = labels.to(device)

        # 前向计算
        outputs = model(images)
        loss = criterion(outputs, labels)
        Loss_list.append(loss)
        # 反向传播
        optimizer.zero_grad()  # 梯度清零
        loss.backward()  # 梯度计算
        optimizer.step()  # 优化参数

        if (i + 1) % 10 == 0:
            print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'
                  .format(epoch + 1, num_epochs, i + 1, total_step, loss.item()))

model.eval()

with torch.no_grad():
    correct = 0
    total = 0
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    print('Test Accuracy of the model on the test images: {} %'.format(100 * correct / total))

torch.save(model.state_dict(), 'GoogLeNet.pt')
print('模型保存成功')
# 最后大概85%的牙子
