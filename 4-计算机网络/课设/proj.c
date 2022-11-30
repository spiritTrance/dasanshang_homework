#include<stdio.h>
#include<string.h>
#include<stdlib.h>
#define True 1
#define False 0
#define DEFAULT_SOURCE_IP 286331153
#define DEFAULT_DESTINATION_IP 286331154
#define OMIT_MESSAGE 2
#define LINK_HEADER_LEN 5
#define LINK_TAIL_LEN 3
#define LINK_BOUND_FLAG 0x7e
#define MTU 1500
typedef char byte;
typedef unsigned int uint;
typedef unsigned short ushort;
// 通过修改下面的False为True来修改对应层次的数据，使其出错被检测到
#define EDITWRONG_TRANS False
#define EDITWRONG_NET   False
#define EDITWRONG_LINK  False
/*
 * 该结构体表示传输层和应用层的头部大小以及
 * 传输层和应用层头部共同的大小
 * 由于网络层部分要分片,所以这个报文可能被分为多个,暂时不考虑下边两层的头部
 */


struct LAYER_LENGTH
{
    ushort APP_LEN;
    ushort TRANS_LEN;
    ushort NET_LEN;
    ushort SUM_LEN;
} LAYER_LEN_WRAPPER;

/*
 * 该结构体表示传输层和应用层的相关
 * binaryMessage表示在层间传输的报文
 */
struct data
{
    char *binaryMessage;            // 二进制报文
} sender, recipient;

/*
 * 该结构体表示伪首部
 */
struct pseudoHead {
    uint sourceIP;      // 源端口
    uint descIP;        // 目的端口
    ushort other;       // 伪首部其他内容
    ushort udpLength;   // UDP长度
} senderPdHead, recipientPdHead;

//================================二进制反码运算=================================
/*
 * 传入一个字节数组的指针和数组的长度,计算校验和
 * 返回校验和,若接受方数据正确返回的校验和是0
 */
ushort checksum(char* a, uint length) {
    ushort ans = 0;
    // 当长度不为偶数个字节时,扩充数组1字节,并填充0
    if (length % 2 != 0) {
        a = (char*)realloc(a, (length + 1) * sizeof(char));
        a[length++] = 0;
    }
    // 计算二进制反码求和
    for (uint i = 0; i < length; i += 2) {
        ushort b;
        memcpy(&b, &a[i], 2);
        uint sum = (uint) ans + (uint) b;
        if (sum > 65535)
        {
            sum %= 65535;
            b = 1;
            sum += (uint) b;
        }
        ans = (ushort) sum;
    }
    // 返回二进制反码求和的反码,即为校验和
    return ~ans;
}


//===================按16进制打印每一个字节,不处理大小端问题======================
void printHex(char* data, uint length) {
    int i;
    for(i = 0; i < length; i++)
    {   // 必须使用unsigned char
        printf("%02x ", (unsigned char) data[i]);
        if(0 == (i + 1) % 16)
            printf("\n");
    }
    printf("\n");
    return;
}
//================================定义函数=======================================
// dataLength为用户输入的数据长度,不包括各个层首部的内容
int appReceive();
int transReceive();
int netReceive();
int linkReceive(ushort dataLength, byte* frame);
int linkSend(ushort dataLength);
int netSend(ushort dataLength);
int transSend(ushort dataLength);
int appSend();
//=================================应用层========================================
/*
 * 应用层协议：面向无连接的协议,默认工作在100端口
 * chat1.0
 * charset:GBK
 * sender:jiangsheng
 * recipient:huanghao
 * Content-Length:40    字节为单位（不超过2^15-1个字节）
 *                      空行表示数据开始，头部共126个字节
 * data                 这是数据部分
 */

/*
 * 功能：发送
 * 返回值：1表示发送成功，0表示发送失败
 */
int appSend () {
    char sendName[31];
    char receiveName[31];
    printf("请输入您的名字（不超过10个字）:");
    scanf("%s", sendName);
    // printf(sendName);
    // printf("%d",sendName[1]);
    printf("请输入接收方的名字（不超过10个字）：");
    scanf("%s", receiveName);
    printf("请输入您想发送的消息（以回车结束）：");
    getchar();
    unsigned short dataLength = 0;      // dataLength为字符的长度(byte)
	char tmp;
	int size = 20;
    int appStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN;     // 应用层开始的位置
	char* message = (char*)malloc(size * sizeof(char));      // 初始分配20个大小的空间
	int n;
	while((tmp = getchar()) != '\n'){
		message[dataLength++] = tmp;
		if(dataLength >= size)
		{
			message = (char*)realloc(message, (size * 2) * sizeof(char));     // 当空间不够，继续追加，空间翻倍
			size *= 2;
		}
	}
    if (dataLength == size) {
        message = (char*)realloc(message, (size + 1) * sizeof(char));  
    }
    else if (dataLength == size - 1) {
        message = (char*)realloc(message, (size + 2) * sizeof(char));  
    }
    message[dataLength++] = '\n';
    message[dataLength++] = 0;
	// printf("%s", message);
    message = (char*)realloc(message, dataLength * sizeof(char));     // 释放掉多余的空间
    // printf("%s", message);
    // printf("%d", message[dataLength - 1]);
    sender.binaryMessage = (char*)malloc((dataLength + LAYER_LEN_WRAPPER.SUM_LEN) * sizeof(char));       // 初始化报文的字节数组
    // 接下来开始填充数据到字节数组中
    printf("\n===============发送方应用层=============\n");
    int cur = appStart;
    char tmp0[9] = "chat1.0\n";
    memcpy(&sender.binaryMessage[cur], tmp0, 9);
    printf("%s", (sender.binaryMessage + cur));
    cur += 9;
    char tmp1[13] = "charset:GBK\n";
    memcpy(&sender.binaryMessage[cur], tmp1, 13);
    printf("%s", (sender.binaryMessage + cur));
    cur += 13;
    char tmp2[8] = "sender:";
    memcpy(&sender.binaryMessage[cur], tmp2, 8);
    printf("%s", (sender.binaryMessage + cur));
    cur += 8;
    memcpy(&sender.binaryMessage[cur], sendName, 31);
    printf("%s", (sender.binaryMessage + cur));
    cur += 31;
    char tmp3[12] = "\nrecipient:";
    memcpy(&sender.binaryMessage[cur], tmp3, 12);
    printf("%s", (sender.binaryMessage + cur));
    cur += 12;
    memcpy(&sender.binaryMessage[cur], receiveName, 31);
    printf("%s", (sender.binaryMessage + cur));
    cur += 31;
    char tmp4[17] = "\nContent-Length:";
    memcpy(&sender.binaryMessage[cur], tmp4, 17);
    printf("%s", (sender.binaryMessage + cur));
    cur += 17;
    memcpy(&sender.binaryMessage[cur], &dataLength, 2);
    printf("%u", dataLength);
    cur += 2;
    char tmp5[3] = "\n\n";
    memcpy(&sender.binaryMessage[cur], tmp5, 3);
    printf("%s", (sender.binaryMessage + cur));
    cur += 3;
    memcpy(&sender.binaryMessage[cur], message, dataLength);
    printf("%s", (sender.binaryMessage + cur));
    return transSend(dataLength);
}

/*
 * 功能：接收
 * 返回值：1表示接收成功，0表示接收失败
 */
int appReceive() {
    int appStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN;
    int cur = appStart;
    char sendName[31];
    char receiveName[31];
    // 打印报文应用层
    printf("\n===============接收方应用层=============\n");
    printf("%s", (recipient.binaryMessage + cur));
    cur += 9;
    printf("%s", (recipient.binaryMessage + cur));
    cur += 13;
    printf("%s", (recipient.binaryMessage + cur));
    cur += 8;
    printf("%s", (recipient.binaryMessage + cur));
    memcpy(sendName, &recipient.binaryMessage[cur], 31);
    cur += 31;
    printf("%s", (recipient.binaryMessage + cur));
    cur += 12;
    printf("%s", (recipient.binaryMessage + cur));
    memcpy(receiveName, &recipient.binaryMessage[cur], 31);
    cur += 31;
    printf("%s", (recipient.binaryMessage + cur));
    cur += 17;
    unsigned short dataLength;
    memcpy(&dataLength, &recipient.binaryMessage[cur], 2);
    printf("%u", dataLength);
    cur += 2;
    printf("%s", (recipient.binaryMessage + cur));
    cur += 3;
    printf("%s", (recipient.binaryMessage + cur));
    char* message = (char*)malloc(dataLength * sizeof(char));
    memcpy(message, &recipient.binaryMessage[cur], dataLength);
    printf("\n您收到来自%s的消息,消息为:\n%s", sendName, message);
    return 1;
}

//================================传输层=============================================
int transSend(unsigned short dataLength) {
    printf("\n===============发送方传输层=============\n");
    int transStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN;
    int cur = transStart;
    // UDP头部
    unsigned short sourcePort = 100;
    unsigned short descPort = 100;
    unsigned short udpLength = dataLength + LAYER_LEN_WRAPPER.APP_LEN + LAYER_LEN_WRAPPER.TRANS_LEN;
    unsigned short cksum = 0;
    // 伪首部
    senderPdHead.sourceIP = 286331153;      // 1.1.1.1
    senderPdHead.descIP = 286331154;        // 1.1.1.2
    senderPdHead.other = 17;
    senderPdHead.udpLength = udpLength;

    memcpy(&sender.binaryMessage[cur], &sourcePort, 2);
    printf("源端口:%u\n",sourcePort);
    cur += 2;
    memcpy(&sender.binaryMessage[cur], &descPort, 2);
    printf("目的端口:%u\n",descPort);
    cur += 2;
    memcpy(&sender.binaryMessage[cur], &udpLength, 2);
    printf("长度:%u\n",udpLength);
    cur += 2;
    memcpy(&sender.binaryMessage[cur], &cksum, 2);

    // 得到需要参与校验和的数据
    char* cptPart = (char*)malloc((udpLength + 12) * sizeof(char));
    memcpy(cptPart, &senderPdHead.sourceIP, 4);
    memcpy(&cptPart[4], &senderPdHead.descIP, 4);
    memcpy(&cptPart[8], &senderPdHead.other, 2);
    memcpy(&cptPart[10], &senderPdHead.udpLength, 2);
    memcpy(&cptPart[12], sender.binaryMessage + transStart, udpLength);
    // 计算检验和
    cksum = checksum(cptPart, udpLength + 12);
    // 填入校验和
    memcpy(&sender.binaryMessage[cur], &cksum, 2);
    // 错误修改实验
    if (EDITWRONG_TRANS){
        sender.binaryMessage[cur - 2] ^= (sender.binaryMessage[cur - 1] + 5);
    }
    printf("校验和:%u\n",cksum);
    printf("\n将报文按16进制展示为:\n");
    printHex(sender.binaryMessage + transStart, udpLength);
    return netSend(dataLength);
}

int transReceive() {
    printf("\n===============接收方传输层=============\n");
    int transStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN;
    int cur = transStart;
    // UDP头部
    unsigned short sourcePort;
    unsigned short descPort;
    unsigned short udpLength;
    unsigned short cksum;
    // 获取头部内容
    memcpy(&sourcePort, &recipient.binaryMessage[cur], 2);
    printf("源端口:%u\n",sourcePort);
    cur += 2;
    memcpy(&descPort, &recipient.binaryMessage[cur], 2);
    printf("目的端口:%u\n",descPort);
    cur += 2;
    memcpy(&udpLength, &recipient.binaryMessage[cur], 2);
    printf("长度:%u\n",udpLength);
    cur += 2;
    memcpy(&cksum, &recipient.binaryMessage[cur], 2);
    printf("校验和:%u",cksum);
    // 伪首部,在网络层封装sourceIP和descIP
    recipientPdHead.other = 17;
    recipientPdHead.udpLength = udpLength;
    // 得到需要参与校验和的数据
    char* cptPart = (char*)malloc((udpLength + 12) * sizeof(char));
    memcpy(cptPart, &recipientPdHead.sourceIP, 4);
    memcpy(&cptPart[4], &recipientPdHead.descIP, 4);
    memcpy(&cptPart[8], &recipientPdHead.other, 2);
    memcpy(&cptPart[10], &recipientPdHead.udpLength, 2);
    memcpy(&cptPart[12], recipient.binaryMessage + transStart, udpLength);
    // 当校验和正确(返回结果为0),打印结果
    if (0 == (cksum = checksum(cptPart, udpLength + 12))) {
        printf(" (校验正确)\n");
        printf("\n将报文按16进制展示为:\n");
        printHex(recipient.binaryMessage + transStart, udpLength);
    }
    else {
        printf("\n校验和出现错误!!!!\n");
        return -1;
    }
    return appReceive();
}

//===============================网络层==============================================
typedef struct netHeader                // 定义IP数据报首部，共固定为20个字节
{
    byte versionAndHeaderLength;        // 版本和首部长度
    byte service;                       // 服务类型
    ushort totLength;                  // 总长度
    ushort counter;                    // 标识
    ushort chipflagAndchipShift;       // 分片标志和片偏移
    byte TTL;                           // 生存时间
    byte protocal;                      // 协议
    ushort headerChecksum;             // 首部检验和
    uint srcIP;                      // 源地址
    uint dstIP;                      // 目的地址
}netHeader;

// 打印网络层数据报头部信息
void printNetHeader(netHeader* header){
    printf("版本为：%u\n", (header->versionAndHeaderLength & 0xf0) >> 4);
    printf("首部长度为：%u个单位\n", (header->versionAndHeaderLength & 0x0f));
    printf("区分服务字段为：%u\n", (header->service));
    printf("总长度为：%u个字节\n", (header->totLength));
    printf("标识为：%u\n", (header->counter));
    printf("标志位为：%03u\n", (header->chipflagAndchipShift & 0xe000) >> 13);
    printf("片偏移为：%u\n", (header->chipflagAndchipShift & 0x1fff));
    printf("TTL为：%u\n", (header->TTL));
    printf("协议字段为：%u\n", header->protocal);
    printf("首部检验和为：%u\n", header->headerChecksum);
    printf("源地址为：%u\n", header->srcIP);
    printf("目的地址为：%u\n", header->dstIP);
}

int netSend(ushort dataLength) {
    printf("\n===============发送方网络层=============\n");
    int netStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN - LAYER_LEN_WRAPPER.NET_LEN;
    netHeader* header = malloc(sizeof(netHeader));
    uint dataLen = dataLength + LAYER_LEN_WRAPPER.APP_LEN + LAYER_LEN_WRAPPER.TRANS_LEN;    // 数据部分的长度
    header->versionAndHeaderLength = 0x45;                      // 制作头部
    header->service = 0x00;
    header->totLength = dataLen + LAYER_LEN_WRAPPER.NET_LEN;    // 包括网络层、运输层、应用层的首部之和以及应用层的数据部分长度
    header->counter = 0;
    header->TTL = 0xff;
    header->protocal = 17;          // 承载的是UDP
    header->headerChecksum = 0;
    header->srcIP = DEFAULT_SOURCE_IP;
    header->dstIP = DEFAULT_DESTINATION_IP;
    // 校验和计算
    header->headerChecksum = checksum((char*)header, LAYER_LEN_WRAPPER.NET_LEN);
    // 复制过程
    memcpy(sender.binaryMessage + netStart, header, LAYER_LEN_WRAPPER.NET_LEN);  // 头部复制
    if (EDITWRONG_NET){
        sender.binaryMessage[netStart + 10] ^= sender.binaryMessage[netStart + 10];
    }
    // 打印中间过程
    printNetHeader(header);
    printf("报文内容为:\n");
    printHex(sender.binaryMessage, header->totLength);
    return linkSend(dataLength);
}

int netReceive() {
    printf("\n===============接收方网络层=============\n");
    int netStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN - LAYER_LEN_WRAPPER.NET_LEN;
    // 检查校验和
    netHeader *header = malloc(sizeof(header));
    ushort *headerLen = malloc(sizeof(ushort));
    memcpy(headerLen, recipient.binaryMessage + netStart, sizeof(ushort));              // 把第一个字节复制过来
    *headerLen = (*headerLen & 0x0f) * 4;                                               // 通过位运算获取首部长度
    memcpy(header, recipient.binaryMessage + netStart, *headerLen);      // 复制首部
    ushort cksum = checksum((char *)header, LAYER_LEN_WRAPPER.NET_LEN);
    if (cksum != 0){       // 校验码结果不为零
        printf("网络层校验码错误！！！");
        return -1;
    }
    printf("网络层校验码正确！！！");
    if (header->TTL == 0){
        printf("TTL为0，丢弃。");
        return -OMIT_MESSAGE;
    }
    ushort headerLength = (header->versionAndHeaderLength & 0x0f);
    uint unsealLen = header->totLength - headerLength * 4;
    printf("网络层接收方的报文为：\n");
    printHex(recipient.binaryMessage + netStart, unsealLen);
    // 伪首部IP地址的获取
    recipientPdHead.sourceIP = header->srcIP;
    recipientPdHead.descIP = header->dstIP;
    return transReceive();
}


//===============================数据链路层===========================================
// PPP 协议帧格式
typedef struct linkHeader{
    byte flagStart;
    byte addressSeg;
    byte ctrlSeg;
    ushort protocal;
} linkHeader;
typedef struct linkTail{
    ushort FCS;
    byte flagEnd;
} linkTail;

int linkDataByteFilling(byte* data, byte* newData, ushort dataLen){        // 透明传输,newData指针在外面就要申请好哦，返回新数据字段的长度
    int newDataLen = 0;
    for (int i = 0; i < dataLen; i++){
        byte *p = data + i;
        if (*p == 0x7E){
            newData[newDataLen++] = 0x7D;
            newData[newDataLen++] = 0x5E;
        }
        else if (*p == 0x7D){
            newData[newDataLen++] = 0x7D;
            newData[newDataLen++] = 0x5D;
        }
        else if (*p < 0x20){
            newData[newDataLen++] = 0x7D;
            newData[newDataLen++] = *p + 0x20;
        }
        else{
            newData[newDataLen++] = *p;
        }
    }
    return newDataLen;
}

int linkDataParser(byte* data, byte* originData, ushort dataLen){         // 接收方数据链路层的[数据部分]实现解码，返回解码后的数据长度
    int readShift = 0;      // data的指针偏移量
    int writeShift = 0;     // originData的指针偏移量
    while(readShift < dataLen){
        byte val = *(data + readShift);
        if (val != 0x7D){
            *(originData + writeShift) = *(data + readShift);
            readShift++;
        }
        else{
            byte nextVal = *(data + readShift + 1);
            if (nextVal == 0x5E){
                *(originData + writeShift) = 0x7E;
            }
            else if (nextVal == 0x5D){
                *(originData + writeShift) = 0x7D;
            }
            else{       // 小于0x20的情况
                *(originData + writeShift) = nextVal - 0x20;
            }
            readShift += 2;
        }
        writeShift++;
    }
    return writeShift;
}

int linkFrameParser(byte* frame, linkHeader* header, linkTail* tail, byte* originData, int* frameLen){       // 对接收方的Frame进行解析，把头部和数据部分拆分出来，返回数据部分的长度
    // 考虑到实际代码实现的第一个一定是0x7E，故不再检测第一个标志字段
    *frameLen = 0;
    byte *p = frame;
    int flagCount = 0;           // 检测到的标志数
    while(flagCount < 2){
        if (*p == LINK_BOUND_FLAG){
            flagCount += 1;
        }
        (*frameLen)++;
        p = frame + (*frameLen);
    }
    int dataLen = (*frameLen) - LINK_HEADER_LEN - LINK_TAIL_LEN;
    byte *data = malloc(dataLen);
    memcpy(header, frame, LINK_HEADER_LEN);
    memcpy(data, frame + LINK_HEADER_LEN, dataLen);
    memcpy(tail, frame + dataLen + LINK_HEADER_LEN, LINK_TAIL_LEN);
    int originDataLen = linkDataParser(data, originData, dataLen);
    return originDataLen;
}

// CRC16查表
byte CRC_HI_TABLE[]={
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40
};
byte CRC_LO_TABLE[]={
0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D, 0xCD,
0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09, 0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A,
0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4,
0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A, 0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29,
0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67,
0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F, 0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68,
0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92,
0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C, 0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B,
0x99, 0x59, 0x58, 0x98, 0x88, 0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80, 0x40
};

ushort CRC16(byte* data, int dataLen){
    byte HI = 0xFF;
    byte LO = 0xFF;
    byte idx;
    while (dataLen--)
    {
        idx = HI ^ *data++;
        HI = LO ^ CRC_HI_TABLE[idx];
        LO = CRC_LO_TABLE[idx];
    }
    return ((HI << 8) | LO) ;
}

void printLinkLayerMsg(linkHeader* header, linkTail* tail){
    printf("地址字段A: %u\n", header->addressSeg);
    printf("控制字段C: %u\n", header->ctrlSeg);
    printf("协议字段: %u\n", header->protocal);
    printf("FCS: %u\n", tail->FCS);
}

int linkSend(ushort dataLength) {
    printf("\n===============发送方数据链路层=============\n");
    linkHeader *header = malloc(sizeof(linkHeader));
    linkTail *tail = malloc(sizeof(linkTail));
    // header
    header->flagStart = LINK_BOUND_FLAG;
    header->addressSeg = 0xff;
    header->ctrlSeg = 0x03;
    header->protocal = 0x0021;
    // 取出网络层的报文段作为数据
    int netStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN - LAYER_LEN_WRAPPER.NET_LEN;     // 网络层的起始指针
    ushort *ipDataLength = malloc(sizeof(ushort));
    memcpy(ipDataLength, sender.binaryMessage + netStart + 2, sizeof(ushort));        // 加2的原因是长度数据在后面
    if (*ipDataLength > MTU){                   // 数据长度检查
        printf("数据链路层数据部分最大长度超过MTU！！！");
        return -1;
    }
    byte *data = malloc(*ipDataLength);
    memcpy(data, sender.binaryMessage + netStart, *ipDataLength);       // 复制网络层报文
    byte *newData = malloc(2 * (*ipDataLength));            // 两倍的空间一定够作为新开辟的空间
    int newDataLen = linkDataByteFilling(data, newData, *ipDataLength);
    // tail
    byte *frame = malloc(LINK_HEADER_LEN + newDataLen + LINK_TAIL_LEN);
    // 复制首部和数据部分
    memcpy(frame, header, LINK_HEADER_LEN);   // 头部
    memcpy(frame + LINK_HEADER_LEN, newData, newDataLen);   // 数据部分
    // 计算CRC
    tail->FCS = CRC16(frame, newDataLen + LINK_HEADER_LEN);
    tail->flagEnd = LINK_BOUND_FLAG;
    // 复制尾部
    memcpy(frame + LINK_HEADER_LEN + newDataLen, tail, LINK_TAIL_LEN);   // 尾部
    // 修改
    if (EDITWRONG_LINK){
        frame[2] ^= (frame[9]);
    }
    // 打印相关信息
    printLinkLayerMsg(header, tail);
    printf("传输帧的数据部分为：\n");
    printHex(newData, newDataLen);
    return linkReceive(dataLength, frame);
}

int linkReceive(ushort dataLength, byte* frame) {
    // 在数据链路层复制报文内容,也可通过文件读取
    printf("\n===============接收方数据链路层=============\n");
    linkHeader *header = malloc(sizeof(linkHeader));
    linkTail *tail = malloc(sizeof(linkTail));
    byte *originData = malloc(MTU);
    int *frameLen = malloc(sizeof(int));
    int originDataLength = linkFrameParser(frame, header, tail, originData, frameLen);
    // 打印信息
    printLinkLayerMsg(header, tail);
    printf("链路层接收方收到的帧的数据部分为：\n");
    printHex(frame + LINK_HEADER_LEN, (uint)(*frameLen - LINK_HEADER_LEN - LINK_TAIL_LEN));
    // FCS检验
    ushort FCScheck = CRC16(frame, *frameLen - LINK_TAIL_LEN);
    ushort FCSrcv = tail->FCS;
    if (FCScheck != FCSrcv){
        printf("数据链路层CRC校验发生错误！！！\n");
        return -1;
    }
    printf("数据链路层CRC校验正确！！！\n");
    recipient.binaryMessage = (byte *)malloc(originDataLength);
    memcpy(recipient.binaryMessage, originData, originDataLength);
    return netReceive();
}

// 功能：初始化各层头部长度
void initHeaderLength(){
    LAYER_LEN_WRAPPER.APP_LEN = 126;
    LAYER_LEN_WRAPPER.TRANS_LEN = 8;
    LAYER_LEN_WRAPPER.NET_LEN = 20;
    LAYER_LEN_WRAPPER.SUM_LEN = LAYER_LEN_WRAPPER.APP_LEN + LAYER_LEN_WRAPPER.TRANS_LEN + LAYER_LEN_WRAPPER.NET_LEN;
}

int main() {
    initHeaderLength();
    int ans = appSend();
}