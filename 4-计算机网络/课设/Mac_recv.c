#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned char byte; //定义帧的单位
typedef unsigned int uint32_t;

//unsigned short 2字节
//unsigned int  4字节
//byte 1字节
// -------------------------运输层的定义-----------------------
byte udp_from_ip[4]={0xc0,0x10,0x01,0x01}; //源ip
byte udp_to_ip[4]={0xc0,0x10,0x01,0x02}; //目的ip
byte zero[1]={0x00}; //全0
byte udp_17[1]={0x17}; //17
byte false_udplen[2]; //数据报长度
//首部
byte from_port[2]; //源端口，需要回信时指定
byte to_port[2]; //目的端口
byte udplen[2]; //用户数据报的长度
byte check_sum[2]; //检验和 暂时为9
// -------------------------网络层的定义-----------------------
byte version_head[1]; //ip数据报版本号为4，首部长度为20bytes
byte diffserv[1]; //区分服务（没用
byte sum_length[2]; //首部和数据部分长度之和
byte identification[2]; //标识字段，计数器
byte flag_divide[2]; //标志和片偏移（没用
byte TTL[1]; //生存时间(没用
byte protocol[1]; //ip数据报携带的数据使用的是UDP协议
byte head_test[2]; //首部检验和，先全部置0
byte from_ip[4]; //源ip地址：192.16.1.1
byte to_ip[4]; //目的i地址：192.16.1.2
// -------------------------链路层的定义-----------------------
byte F[1]; //F
byte A[1]; //A
byte C[1]; //C
byte type[2]; //类型
byte FCS[2];   //接收方生成的帧校验序列
byte frame[1508]; //用于存储读取到的帧

//CRC查表法 生成码表+校验
byte auchCRCHi[]={
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40
};
byte auchCRCLo[]={
0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06,
0x07, 0xC7, 0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D, 0xCD,
0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A,
0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC, 0x14, 0xD4,
0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3,
0xF2, 0x32, 0x36, 0xF6, 0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4,
0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29,
0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF, 0x2D, 0xED,
0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60,
0x61, 0xA1, 0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67,
0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68,
0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A, 0xBA, 0xBE, 0x7E,
0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71,
0x70, 0xB0, 0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92,
0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B,
0x99, 0x59, 0x58, 0x98, 0x88, 0x48, 0x49, 0x89, 0x4B, 0x8B,
0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42,
0x43, 0x83, 0x41, 0x81, 0x80, 0x40
};

// 检验udp数据报的检验和
void test_checksum(byte* udp_from_ip, byte* udp_to_ip,byte* zero, byte* udp_17,
byte* false_udplen, byte* from_port, byte* to_port,byte* udplen, byte* check_sum,
byte* data_app_to_trans, unsigned short udp_data_len, byte* temp_udp_checksum){
    uint32_t temp1=(udp_from_ip[0] << 8) | udp_from_ip[1];
    uint32_t temp2=(udp_from_ip[2] << 8) | udp_from_ip[3];
    uint32_t temp3=(udp_to_ip[0] << 8) | udp_to_ip[1];
    uint32_t temp4=(udp_to_ip[2] << 8) | udp_to_ip[3];
    uint32_t temp5=(zero[0] << 8) | udp_17[0];
    uint32_t temp6=(false_udplen[0] << 8) | false_udplen[1];
    uint32_t temp7=(from_port[0] << 8) | from_port[1];
    uint32_t temp8=(to_port[0] << 8) | to_port[1];
    uint32_t temp9=(udplen[0] << 8) | udplen[1];
    uint32_t temp10=(check_sum[0] << 8) | check_sum[1];
    int length = strlen(data_app_to_trans);  //可能要改
    uint32_t temp[1500];
    int i=0;
    int count=0;
    while (length!=0 && length!=1){
        temp[count]=(data_app_to_trans[i] << 8) | data_app_to_trans[i+1];
        count+=1;
        i+=2;
        length-=2;
    }
    if (length==1){
        byte tp_zero[1]={0x00};
        temp[count]=(data_app_to_trans[i] << 8) | tp_zero[0];
        count+=1;
    }
    uint32_t res=temp1+temp2+temp3+temp4+temp5+temp6+temp7+temp8+temp9+temp10;
    for (int j=0;j<count;j+=1){
        res+=temp[j];
    }
    res=~res;
    uint32_t tp;
    tp = res & 0xffff;
    temp_udp_checksum[0] = tp >> 8;
    temp_udp_checksum[1] = tp & 0xff;
}

// 检验ip数据报的首部和
void test_head_test(byte* version_head,byte* diffserv,byte* sum_length,
byte* identification, byte* flag_divide, byte* TTL, byte* protocol,
byte* head_test, byte* from_ip, byte* to_ip,byte* temp_ip_head_test){
    uint32_t temp1=(version_head[0] << 8) | diffserv[0];
    uint32_t temp2=(sum_length[0] << 8) | sum_length[1];
    uint32_t temp3=(identification[0] << 8) | identification[1];
    uint32_t temp4=(flag_divide[0] << 8) | flag_divide[1];
    uint32_t temp5=(TTL[0] << 8) | protocol[0];
    uint32_t temp6=(head_test[0] << 8) | head_test[1];
    uint32_t temp7=(from_ip[0] << 8) | from_ip[1];
    uint32_t temp8=(from_ip[2] << 8) | from_ip[3];
    uint32_t temp9=(to_ip[0] << 8) | to_ip[1];
    uint32_t temp10=(to_ip[2] << 8) | to_ip[3];
    // printf("temp1: %04x\n",temp7);
    uint32_t res=temp1+temp2+temp3+temp4+temp5+temp6+temp7+temp8+temp9+temp10;
    res=~res; //取反
    uint32_t tp;
    tp = res & 0xffff;
    temp_ip_head_test[0] = tp >> 8;
    temp_ip_head_test[1] = tp & 0xff; 
}

unsigned short CRC16(byte* data, unsigned short datalen)
{
    byte uchCRCHi = 0xFF ;
    byte uchCRCLo = 0xFF ;
    byte uIndex ;
    while (datalen--)
    {
        uIndex = uchCRCHi ^ *data++;
        uchCRCHi = uchCRCLo ^ auchCRCHi[uIndex];
        uchCRCLo = auchCRCLo[uIndex];
    }
    return (uchCRCHi << 8 | uchCRCLo) ;
};

// 打印udp报文
void udpshow(byte* from_port,byte* to_port,byte* udplen, byte* check_sum,
unsigned short udp_data_len,byte* data_app_to_trans){
    printf("解析报文结构: \n");
    printf("源端口: %02x%02x\n",from_port[0],from_port[1]);
    printf("目的端口: %02x%02x\n",to_port[0],to_port[1]);
    printf("报文总长度: %02x%02x\n",udplen[0],udplen[1]);
    printf("检验和: %02x%02x\n",check_sum[0],check_sum[1]);
    printf("运输层数据部分: ");
    for (int i=0;i<udp_data_len;i+=1){
        printf("%02x",data_app_to_trans[i]);
    }
    printf("\n");
}

// 打印ip数据报
void ipshow(unsigned short gooddatalen,byte* version_head, byte* diffserv, byte* sum_length,
byte* identification, byte* flag_divide, byte* TTL, byte* protocol, byte* head_test,byte* from_ip,
byte* to_ip,unsigned short data_trans_ip_len,byte* data_trans_to_ip){
    printf("解析数据报结构：\n");
    printf("版本号，首部长度：%02x\n",version_head[0]);
    printf("区分服务：%02x \n",diffserv[0]);
    printf("总长度：%02x%02x \n",sum_length[0],sum_length[1]);
    printf("标识：%02x%02x \n",identification[0],identification[1]);
    printf("标志和片偏移：%02x%02x \n",flag_divide[0],flag_divide[1]);
    printf("生存时间：%02x \n",TTL[0]);
    printf("协议：%02x \n",protocol[0]);
    printf("首部检验和：%02x%02x \n",head_test[0],head_test[1]);
    printf("源地址：%02x%02x%02x%02x \n",from_ip[0],from_ip[1],from_ip[2],from_ip[3]);
    printf("目标地址：%02x%02x%02x%02x \n",to_ip[0],to_ip[1],to_ip[2],to_ip[3]);
    printf("网络层数据部分：");
    for (int i=0;i<data_trans_ip_len;i+=1){
        printf("%02x",data_trans_to_ip[i]);
    }
    printf("\n");

}

//打印帧
void frameshow(unsigned short frameLen, byte *F, byte *A, byte *C, byte *type, byte *data,byte *FCS, unsigned short datalen,byte *F_later)
{
    printf(" 解析帧结构: ");
    printf("\n 帧长: %u",frameLen);
    printf("\n F字段: %02x",F[0]);
    printf("\n A字段: %02x",A[0]);
    printf("\n C字段: %02x",C[0]);
    if(type[0]==0x00&&type[1]==0x21)
    {
        printf("\n 信息字段是IP数据报");
    }
    else if(type[0]==0xc0&&type[1]==0x21)
    {
        printf("\n 信息字段是PPP链路控制协议LCP的数据");
    }
    else if(type[0]==0x80&&type[1]==0x21)
    {
        printf("\n 信息字段是网络层的控制数据");
    }
    printf("\n Type: %02x%02x",type[0],type[1]);
    printf("\n 信息部分: ");
    for(int i=0;i<datalen;i++)
    {
        printf("%02x",data[i]);
    }
    printf("\n FCS: %02x%02X",FCS[0],FCS[1]);
    printf("\n F字段: %02x",F_later[0]);
}

int main()
{
    FILE *fp = fopen("mac.frm", "r");
    unsigned short frameLen;
    int num = 0; //记录帧的数量

    while (fread(&frameLen, sizeof(frameLen), 1, fp)) //读取帧的长度(第一个字节)
    {
        // 数据链路层解析
        if (!frameLen)
            break;
        num++;
        fread(frame, sizeof(byte), frameLen, fp); //读取帧
        // CRC校验
        unsigned short FCS_int;
        FCS_int = CRC16(frame, frameLen - 3);
        //byte FCS[2]; 是接收方生成的帧校验序列
        byte FCS_frame[2]; //接受到的帧的帧校验序列
        memcpy(&FCS, &FCS_int, sizeof(FCS_int));
        memcpy(&FCS_frame, &frame[frameLen - 3], 2);
        if (FCS[1] != FCS_frame[1] || FCS[0] != FCS_frame[0])
        {
            printf("帧 %d :\n CRC帧校验序列不匹配,传输出错.\n", num);
            printf("------------------------------------------\n");
            continue;
        }
        //解析帧
        memcpy(&F, &frame[0], 1);
        memcpy(&A, &frame[1], 1);
        memcpy(&C, &frame[2], 1);
        memcpy(&type, &frame[3], 2);
        unsigned short datalen = frameLen - 8;
        byte data[datalen];
        memcpy(&data,&frame[5],datalen);

        int count=0;
        for(int i=0;i<datalen;i++)
        {
            if((data[i]==0x7D&&data[i+1]==0x5E)||(data[i]==0x7D&&data[i+1]==0x5D)||(data[i]==0x7D&&data[i+1]<0x20))
            {
                count++;
            }
        }

        byte good_data[datalen-count];
        unsigned short gooddatalen = sizeof(good_data);
        printf("datalen: %d\n",gooddatalen);
        printf("count: %d\n",count);

        int j=0;
        for(int i=0;i<datalen;i++)
        {
            if(data[i]==0x7D&&data[i+1]==0x5E)
            {
                good_data[j] = 0x7E;
                j++;
                i++;
            }
            else if(data[i]==0x7D&&data[i+1]==0x5D)
            {
                good_data[j] = 0x7D;
                j++;
                i++;
            }
            else if(data[i]==0x7D&&data[i+1]<0x20)
            {
                good_data[j] = data[i+1];
                j++;
                i++;
            }
            else
            {
                good_data[j] = data[i];
                j++;
            }
        }
        byte F_later[1];
        memcpy(&F_later,&frame[datalen+7],1);
        if(F_later[0]!=F[0])
        {
            printf("帧 %d :\n 传输出错. 不接收帧\n", num);
            printf("------------------------------------------\n");
            continue;
        }
        //打印帧
        printf("帧 %d :\n 帧的长度: %u 接收成功.\n", num, frameLen-count);
        frameshow(frameLen, F, A,C, type, good_data,FCS, gooddatalen,F_later);
        printf("\n------------------------------------------\n");


        // 网络层解析
        unsigned short ip_data_len=gooddatalen-20;
        byte data_trans_to_ip[gooddatalen-20]; //运输层传入ip的数据
        memcpy(version_head,&good_data[0],1);
        memcpy(diffserv,&good_data[1],1);
        memcpy(sum_length,&good_data[2],2);
        memcpy(identification,&good_data[4],2);
        memcpy(flag_divide,&good_data[6],2);
        memcpy(TTL,&good_data[8],1);
        memcpy(protocol,&good_data[9],1);
        memcpy(head_test,&good_data[10],2);
        memcpy(from_ip,&good_data[12],4);
        memcpy(to_ip,&good_data[16],4);
        memcpy(data_trans_to_ip,&good_data[20],gooddatalen-20);
        byte temp_ip_head_test[2];
        test_head_test(version_head,diffserv,sum_length,identification,flag_divide,TTL,protocol,head_test,from_ip,to_ip,temp_ip_head_test);
        if (temp_ip_head_test[0] != 0x00 || temp_ip_head_test[1]!=0x00){
            printf("首部检验和错误\n");
            printf("%02x%02x\n",temp_ip_head_test[0],temp_ip_head_test[1]);
        }
        else{
            printf("首部检验和成功\n");
        }
        printf("ip数据报接收成功\n");
        ipshow(gooddatalen,version_head,diffserv,sum_length,identification,flag_divide,TTL,protocol,head_test,from_ip,to_ip,gooddatalen-20,data_trans_to_ip);
        printf("------------------------------------------\n");

        
        //运输层解析
        unsigned short udp_data_len=ip_data_len-8;
        byte data_app_to_trans[udp_data_len];
        memcpy(from_port,&data_trans_to_ip[0],2);
        memcpy(to_port,&data_trans_to_ip[2],2);
        memcpy(udplen,&data_trans_to_ip[4],2);
        memcpy(check_sum,&data_trans_to_ip[6],2);
        memcpy(data_app_to_trans,&data_trans_to_ip[8],udp_data_len);
        memcpy(false_udplen,udplen,2);
        byte temp_udp_checksum[2];
        test_checksum(udp_from_ip,udp_to_ip,zero,udp_17,false_udplen,from_port,to_port,udplen,check_sum,data_app_to_trans,udp_data_len,temp_udp_checksum);
        if (temp_udp_checksum[0] != 0x00 || temp_udp_checksum[1] != 0x00){
            printf("检验和验证错误\n");
        }
        else{
            printf("检验和验证正确\n");
        }
        printf("udp数据报接收成功\n");
        udpshow(from_port,to_port,udplen,check_sum,udp_data_len,data_app_to_trans);

    }
    fclose(fp);

    return 0;
}