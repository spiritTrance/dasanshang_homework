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
// ͨ���޸������FalseΪTrue���޸Ķ�Ӧ��ε����ݣ�ʹ�������⵽
#define EDITWRONG_TRANS False
#define EDITWRONG_NET   False
#define EDITWRONG_LINK  False
/*
 * �ýṹ���ʾ������Ӧ�ò��ͷ����С�Լ�
 * ������Ӧ�ò�ͷ����ͬ�Ĵ�С
 * ��������㲿��Ҫ��Ƭ,����������Ŀ��ܱ���Ϊ���,��ʱ�������±������ͷ��
 */


struct LAYER_LENGTH
{
    ushort APP_LEN;
    ushort TRANS_LEN;
    ushort NET_LEN;
    ushort SUM_LEN;
} LAYER_LEN_WRAPPER;

/*
 * �ýṹ���ʾ������Ӧ�ò�����
 * binaryMessage��ʾ�ڲ�䴫��ı���
 */
struct data
{
    char *binaryMessage;            // �����Ʊ���
} sender, recipient;

/*
 * �ýṹ���ʾα�ײ�
 */
struct pseudoHead {
    uint sourceIP;      // Դ�˿�
    uint descIP;        // Ŀ�Ķ˿�
    ushort other;       // α�ײ���������
    ushort udpLength;   // UDP����
} senderPdHead, recipientPdHead;

//================================�����Ʒ�������=================================
/*
 * ����һ���ֽ������ָ�������ĳ���,����У���
 * ����У���,�����ܷ�������ȷ���ص�У�����0
 */
ushort checksum(char* a, uint length) {
    ushort ans = 0;
    // �����Ȳ�Ϊż�����ֽ�ʱ,��������1�ֽ�,�����0
    if (length % 2 != 0) {
        a = (char*)realloc(a, (length + 1) * sizeof(char));
        a[length++] = 0;
    }
    // ��������Ʒ������
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
    // ���ض����Ʒ�����͵ķ���,��ΪУ���
    return ~ans;
}


//===================��16���ƴ�ӡÿһ���ֽ�,�������С������======================
void printHex(char* data, uint length) {
    int i;
    for(i = 0; i < length; i++)
    {   // ����ʹ��unsigned char
        printf("%02x ", (unsigned char) data[i]);
        if(0 == (i + 1) % 16)
            printf("\n");
    }
    printf("\n");
    return;
}
//================================���庯��=======================================
// dataLengthΪ�û���������ݳ���,�������������ײ�������
int appReceive();
int transReceive();
int netReceive();
int linkReceive(ushort dataLength, byte* frame);
int linkSend(ushort dataLength);
int netSend(ushort dataLength);
int transSend(ushort dataLength);
int appSend();
//=================================Ӧ�ò�========================================
/*
 * Ӧ�ò�Э�飺���������ӵ�Э��,Ĭ�Ϲ�����100�˿�
 * chat1.0
 * charset:GBK
 * sender:jiangsheng
 * recipient:huanghao
 * Content-Length:40    �ֽ�Ϊ��λ��������2^15-1���ֽڣ�
 *                      ���б�ʾ���ݿ�ʼ��ͷ����126���ֽ�
 * data                 �������ݲ���
 */

/*
 * ���ܣ�����
 * ����ֵ��1��ʾ���ͳɹ���0��ʾ����ʧ��
 */
int appSend () {
    char sendName[31];
    char receiveName[31];
    printf("�������������֣�������10���֣�:");
    scanf("%s", sendName);
    // printf(sendName);
    // printf("%d",sendName[1]);
    printf("��������շ������֣�������10���֣���");
    scanf("%s", receiveName);
    printf("���������뷢�͵���Ϣ���Իس���������");
    getchar();
    unsigned short dataLength = 0;      // dataLengthΪ�ַ��ĳ���(byte)
	char tmp;
	int size = 20;
    int appStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN;     // Ӧ�ò㿪ʼ��λ��
	char* message = (char*)malloc(size * sizeof(char));      // ��ʼ����20����С�Ŀռ�
	int n;
	while((tmp = getchar()) != '\n'){
		message[dataLength++] = tmp;
		if(dataLength >= size)
		{
			message = (char*)realloc(message, (size * 2) * sizeof(char));     // ���ռ䲻��������׷�ӣ��ռ䷭��
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
    message = (char*)realloc(message, dataLength * sizeof(char));     // �ͷŵ�����Ŀռ�
    // printf("%s", message);
    // printf("%d", message[dataLength - 1]);
    sender.binaryMessage = (char*)malloc((dataLength + LAYER_LEN_WRAPPER.SUM_LEN) * sizeof(char));       // ��ʼ�����ĵ��ֽ�����
    // ��������ʼ������ݵ��ֽ�������
    printf("\n===============���ͷ�Ӧ�ò�=============\n");
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
 * ���ܣ�����
 * ����ֵ��1��ʾ���ճɹ���0��ʾ����ʧ��
 */
int appReceive() {
    int appStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN;
    int cur = appStart;
    char sendName[31];
    char receiveName[31];
    // ��ӡ����Ӧ�ò�
    printf("\n===============���շ�Ӧ�ò�=============\n");
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
    printf("\n���յ�����%s����Ϣ,��ϢΪ:\n%s", sendName, message);
    return 1;
}

//================================�����=============================================
int transSend(unsigned short dataLength) {
    printf("\n===============���ͷ������=============\n");
    int transStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN;
    int cur = transStart;
    // UDPͷ��
    unsigned short sourcePort = 100;
    unsigned short descPort = 100;
    unsigned short udpLength = dataLength + LAYER_LEN_WRAPPER.APP_LEN + LAYER_LEN_WRAPPER.TRANS_LEN;
    unsigned short cksum = 0;
    // α�ײ�
    senderPdHead.sourceIP = 286331153;      // 1.1.1.1
    senderPdHead.descIP = 286331154;        // 1.1.1.2
    senderPdHead.other = 17;
    senderPdHead.udpLength = udpLength;

    memcpy(&sender.binaryMessage[cur], &sourcePort, 2);
    printf("Դ�˿�:%u\n",sourcePort);
    cur += 2;
    memcpy(&sender.binaryMessage[cur], &descPort, 2);
    printf("Ŀ�Ķ˿�:%u\n",descPort);
    cur += 2;
    memcpy(&sender.binaryMessage[cur], &udpLength, 2);
    printf("����:%u\n",udpLength);
    cur += 2;
    memcpy(&sender.binaryMessage[cur], &cksum, 2);

    // �õ���Ҫ����У��͵�����
    char* cptPart = (char*)malloc((udpLength + 12) * sizeof(char));
    memcpy(cptPart, &senderPdHead.sourceIP, 4);
    memcpy(&cptPart[4], &senderPdHead.descIP, 4);
    memcpy(&cptPart[8], &senderPdHead.other, 2);
    memcpy(&cptPart[10], &senderPdHead.udpLength, 2);
    memcpy(&cptPart[12], sender.binaryMessage + transStart, udpLength);
    // ��������
    cksum = checksum(cptPart, udpLength + 12);
    // ����У���
    memcpy(&sender.binaryMessage[cur], &cksum, 2);
    // �����޸�ʵ��
    if (EDITWRONG_TRANS){
        sender.binaryMessage[cur - 2] ^= (sender.binaryMessage[cur - 1] + 5);
    }
    printf("У���:%u\n",cksum);
    printf("\n�����İ�16����չʾΪ:\n");
    printHex(sender.binaryMessage + transStart, udpLength);
    return netSend(dataLength);
}

int transReceive() {
    printf("\n===============���շ������=============\n");
    int transStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN;
    int cur = transStart;
    // UDPͷ��
    unsigned short sourcePort;
    unsigned short descPort;
    unsigned short udpLength;
    unsigned short cksum;
    // ��ȡͷ������
    memcpy(&sourcePort, &recipient.binaryMessage[cur], 2);
    printf("Դ�˿�:%u\n",sourcePort);
    cur += 2;
    memcpy(&descPort, &recipient.binaryMessage[cur], 2);
    printf("Ŀ�Ķ˿�:%u\n",descPort);
    cur += 2;
    memcpy(&udpLength, &recipient.binaryMessage[cur], 2);
    printf("����:%u\n",udpLength);
    cur += 2;
    memcpy(&cksum, &recipient.binaryMessage[cur], 2);
    printf("У���:%u",cksum);
    // α�ײ�,��������װsourceIP��descIP
    recipientPdHead.other = 17;
    recipientPdHead.udpLength = udpLength;
    // �õ���Ҫ����У��͵�����
    char* cptPart = (char*)malloc((udpLength + 12) * sizeof(char));
    memcpy(cptPart, &recipientPdHead.sourceIP, 4);
    memcpy(&cptPart[4], &recipientPdHead.descIP, 4);
    memcpy(&cptPart[8], &recipientPdHead.other, 2);
    memcpy(&cptPart[10], &recipientPdHead.udpLength, 2);
    memcpy(&cptPart[12], recipient.binaryMessage + transStart, udpLength);
    // ��У�����ȷ(���ؽ��Ϊ0),��ӡ���
    if (0 == (cksum = checksum(cptPart, udpLength + 12))) {
        printf(" (У����ȷ)\n");
        printf("\n�����İ�16����չʾΪ:\n");
        printHex(recipient.binaryMessage + transStart, udpLength);
    }
    else {
        printf("\nУ��ͳ��ִ���!!!!\n");
        return -1;
    }
    return appReceive();
}

//===============================�����==============================================
typedef struct netHeader                // ����IP���ݱ��ײ������̶�Ϊ20���ֽ�
{
    byte versionAndHeaderLength;        // �汾���ײ�����
    byte service;                       // ��������
    ushort totLength;                  // �ܳ���
    ushort counter;                    // ��ʶ
    ushort chipflagAndchipShift;       // ��Ƭ��־��Ƭƫ��
    byte TTL;                           // ����ʱ��
    byte protocal;                      // Э��
    ushort headerChecksum;             // �ײ������
    uint srcIP;                      // Դ��ַ
    uint dstIP;                      // Ŀ�ĵ�ַ
}netHeader;

// ��ӡ��������ݱ�ͷ����Ϣ
void printNetHeader(netHeader* header){
    printf("�汾Ϊ��%u\n", (header->versionAndHeaderLength & 0xf0) >> 4);
    printf("�ײ�����Ϊ��%u����λ\n", (header->versionAndHeaderLength & 0x0f));
    printf("���ַ����ֶ�Ϊ��%u\n", (header->service));
    printf("�ܳ���Ϊ��%u���ֽ�\n", (header->totLength));
    printf("��ʶΪ��%u\n", (header->counter));
    printf("��־λΪ��%03u\n", (header->chipflagAndchipShift & 0xe000) >> 13);
    printf("Ƭƫ��Ϊ��%u\n", (header->chipflagAndchipShift & 0x1fff));
    printf("TTLΪ��%u\n", (header->TTL));
    printf("Э���ֶ�Ϊ��%u\n", header->protocal);
    printf("�ײ������Ϊ��%u\n", header->headerChecksum);
    printf("Դ��ַΪ��%u\n", header->srcIP);
    printf("Ŀ�ĵ�ַΪ��%u\n", header->dstIP);
}

int netSend(ushort dataLength) {
    printf("\n===============���ͷ������=============\n");
    int netStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN - LAYER_LEN_WRAPPER.NET_LEN;
    netHeader* header = malloc(sizeof(netHeader));
    uint dataLen = dataLength + LAYER_LEN_WRAPPER.APP_LEN + LAYER_LEN_WRAPPER.TRANS_LEN;    // ���ݲ��ֵĳ���
    header->versionAndHeaderLength = 0x45;                      // ����ͷ��
    header->service = 0x00;
    header->totLength = dataLen + LAYER_LEN_WRAPPER.NET_LEN;    // ��������㡢����㡢Ӧ�ò���ײ�֮���Լ�Ӧ�ò�����ݲ��ֳ���
    header->counter = 0;
    header->TTL = 0xff;
    header->protocal = 17;          // ���ص���UDP
    header->headerChecksum = 0;
    header->srcIP = DEFAULT_SOURCE_IP;
    header->dstIP = DEFAULT_DESTINATION_IP;
    // У��ͼ���
    header->headerChecksum = checksum((char*)header, LAYER_LEN_WRAPPER.NET_LEN);
    // ���ƹ���
    memcpy(sender.binaryMessage + netStart, header, LAYER_LEN_WRAPPER.NET_LEN);  // ͷ������
    if (EDITWRONG_NET){
        sender.binaryMessage[netStart + 10] ^= sender.binaryMessage[netStart + 10];
    }
    // ��ӡ�м����
    printNetHeader(header);
    printf("��������Ϊ:\n");
    printHex(sender.binaryMessage, header->totLength);
    return linkSend(dataLength);
}

int netReceive() {
    printf("\n===============���շ������=============\n");
    int netStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN - LAYER_LEN_WRAPPER.NET_LEN;
    // ���У���
    netHeader *header = malloc(sizeof(header));
    ushort *headerLen = malloc(sizeof(ushort));
    memcpy(headerLen, recipient.binaryMessage + netStart, sizeof(ushort));              // �ѵ�һ���ֽڸ��ƹ���
    *headerLen = (*headerLen & 0x0f) * 4;                                               // ͨ��λ�����ȡ�ײ�����
    memcpy(header, recipient.binaryMessage + netStart, *headerLen);      // �����ײ�
    ushort cksum = checksum((char *)header, LAYER_LEN_WRAPPER.NET_LEN);
    if (cksum != 0){       // У��������Ϊ��
        printf("�����У������󣡣���");
        return -1;
    }
    printf("�����У������ȷ������");
    if (header->TTL == 0){
        printf("TTLΪ0��������");
        return -OMIT_MESSAGE;
    }
    ushort headerLength = (header->versionAndHeaderLength & 0x0f);
    uint unsealLen = header->totLength - headerLength * 4;
    printf("�������շ��ı���Ϊ��\n");
    printHex(recipient.binaryMessage + netStart, unsealLen);
    // α�ײ�IP��ַ�Ļ�ȡ
    recipientPdHead.sourceIP = header->srcIP;
    recipientPdHead.descIP = header->dstIP;
    return transReceive();
}


//===============================������·��===========================================
// PPP Э��֡��ʽ
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

int linkDataByteFilling(byte* data, byte* newData, ushort dataLen){        // ͸������,newDataָ���������Ҫ�����Ŷ�������������ֶεĳ���
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

int linkDataParser(byte* data, byte* originData, ushort dataLen){         // ���շ�������·���[���ݲ���]ʵ�ֽ��룬���ؽ��������ݳ���
    int readShift = 0;      // data��ָ��ƫ����
    int writeShift = 0;     // originData��ָ��ƫ����
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
            else{       // С��0x20�����
                *(originData + writeShift) = nextVal - 0x20;
            }
            readShift += 2;
        }
        writeShift++;
    }
    return writeShift;
}

int linkFrameParser(byte* frame, linkHeader* header, linkTail* tail, byte* originData, int* frameLen){       // �Խ��շ���Frame���н�������ͷ�������ݲ��ֲ�ֳ������������ݲ��ֵĳ���
    // ���ǵ�ʵ�ʴ���ʵ�ֵĵ�һ��һ����0x7E���ʲ��ټ���һ����־�ֶ�
    *frameLen = 0;
    byte *p = frame;
    int flagCount = 0;           // ��⵽�ı�־��
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

// CRC16���
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
    printf("��ַ�ֶ�A: %u\n", header->addressSeg);
    printf("�����ֶ�C: %u\n", header->ctrlSeg);
    printf("Э���ֶ�: %u\n", header->protocal);
    printf("FCS: %u\n", tail->FCS);
}

int linkSend(ushort dataLength) {
    printf("\n===============���ͷ�������·��=============\n");
    linkHeader *header = malloc(sizeof(linkHeader));
    linkTail *tail = malloc(sizeof(linkTail));
    // header
    header->flagStart = LINK_BOUND_FLAG;
    header->addressSeg = 0xff;
    header->ctrlSeg = 0x03;
    header->protocal = 0x0021;
    // ȡ�������ı��Ķ���Ϊ����
    int netStart = LAYER_LEN_WRAPPER.SUM_LEN - LAYER_LEN_WRAPPER.APP_LEN - LAYER_LEN_WRAPPER.TRANS_LEN - LAYER_LEN_WRAPPER.NET_LEN;     // ��������ʼָ��
    ushort *ipDataLength = malloc(sizeof(ushort));
    memcpy(ipDataLength, sender.binaryMessage + netStart + 2, sizeof(ushort));        // ��2��ԭ���ǳ��������ں���
    if (*ipDataLength > MTU){                   // ���ݳ��ȼ��
        printf("������·�����ݲ�����󳤶ȳ���MTU������");
        return -1;
    }
    byte *data = malloc(*ipDataLength);
    memcpy(data, sender.binaryMessage + netStart, *ipDataLength);       // ��������㱨��
    byte *newData = malloc(2 * (*ipDataLength));            // �����Ŀռ�һ������Ϊ�¿��ٵĿռ�
    int newDataLen = linkDataByteFilling(data, newData, *ipDataLength);
    // tail
    byte *frame = malloc(LINK_HEADER_LEN + newDataLen + LINK_TAIL_LEN);
    // �����ײ������ݲ���
    memcpy(frame, header, LINK_HEADER_LEN);   // ͷ��
    memcpy(frame + LINK_HEADER_LEN, newData, newDataLen);   // ���ݲ���
    // ����CRC
    tail->FCS = CRC16(frame, newDataLen + LINK_HEADER_LEN);
    tail->flagEnd = LINK_BOUND_FLAG;
    // ����β��
    memcpy(frame + LINK_HEADER_LEN + newDataLen, tail, LINK_TAIL_LEN);   // β��
    // �޸�
    if (EDITWRONG_LINK){
        frame[2] ^= (frame[9]);
    }
    // ��ӡ�����Ϣ
    printLinkLayerMsg(header, tail);
    printf("����֡�����ݲ���Ϊ��\n");
    printHex(newData, newDataLen);
    return linkReceive(dataLength, frame);
}

int linkReceive(ushort dataLength, byte* frame) {
    // ��������·�㸴�Ʊ�������,Ҳ��ͨ���ļ���ȡ
    printf("\n===============���շ�������·��=============\n");
    linkHeader *header = malloc(sizeof(linkHeader));
    linkTail *tail = malloc(sizeof(linkTail));
    byte *originData = malloc(MTU);
    int *frameLen = malloc(sizeof(int));
    int originDataLength = linkFrameParser(frame, header, tail, originData, frameLen);
    // ��ӡ��Ϣ
    printLinkLayerMsg(header, tail);
    printf("��·����շ��յ���֡�����ݲ���Ϊ��\n");
    printHex(frame + LINK_HEADER_LEN, (uint)(*frameLen - LINK_HEADER_LEN - LINK_TAIL_LEN));
    // FCS����
    ushort FCScheck = CRC16(frame, *frameLen - LINK_TAIL_LEN);
    ushort FCSrcv = tail->FCS;
    if (FCScheck != FCSrcv){
        printf("������·��CRCУ�鷢�����󣡣���\n");
        return -1;
    }
    printf("������·��CRCУ����ȷ������\n");
    recipient.binaryMessage = (byte *)malloc(originDataLength);
    memcpy(recipient.binaryMessage, originData, originDataLength);
    return netReceive();
}

// ���ܣ���ʼ������ͷ������
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