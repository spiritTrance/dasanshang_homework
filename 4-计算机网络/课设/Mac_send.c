#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>

#define MAX 1500            //数据部分最大长度
typedef unsigned char byte; //定义帧的单位
typedef unsigned int uint32_t;
//unsigned short 2字节
//unsigned int  4字节
//byte 1字节
// -------------------------运输层的定义-----------------------
// 伪首部定义
byte udp_from_ip[4]={0xc0,0x10,0x01,0x01}; //源ip
byte udp_to_ip[4]={0xc0,0x10,0x01,0x02}; //目的ip
byte zero[1]={0x00}; //全0
byte udp_17[1]={0x17}; //17
byte false_udplen[2]; //数据报长度
//首部
byte from_port[2]={0x01,0x45}; //源端口，需要回信时指定
byte to_port[2]={0x02, 0x8b}; //目的端口
byte udplen[2]; //用户数据报的长度
byte check_sum[2]={0x00,0x00}; //检验和 暂时为9
// -------------------------网络层的定义-----------------------
byte version_head[1] = {0x45}; //ip数据报版本号为4，首部长度为20bytes
byte diffserv[1] = {0x00}; //区分服务（没用
byte sum_length[2]; //首部和数据部分长度之和
byte identification[2]={0X00,0X01}; //标识字段，计数器
byte flag_divide[2]={0x00,0x00}; //标志和片偏移（没用
byte TTL[1]={0x80}; //生存时间(没用
byte protocol[1]={0x17}; //ip数据报携带的数据使用的是UDP协议
byte head_test[2]={0x00,0x00}; //首部检验和，先全部置0
byte from_ip[4]={0xc0,0x10,0x01,0x01}; //源ip地址：192.16.1.1
byte to_ip[4]={0xc0,0x10,0x01,0x02}; //目的i地址：192.16.1.2

// -------------------------数据链路层的定义-----------------------
//首部
byte F[1] = {0x7E}; //F
byte A[1] = {0xFF}; //A
byte C[1] = {0x03}; //C
byte type[2] = {0x00,0x21}; //2字节, 协议 , 当其为0x0021时，PPP帧的信息字段就是IP数据报。
//若为0xC021，则信息字段是PPP链路控制协议LCP的数据，而0x8021表示是网络层的控制数据。 

// //测试数据部分
// byte data[] = {
//     //用于测试的数据部分 length = 10
//     0x10, //这里要变为0x7D,0x10
//     0xE0,
//     0x4C,
//     0x70,
//     0x7E, //这里要变为0x7E,0x5E
//     0x7D, //这里要变为0x7D,0x5D
//     0xE0,
//     0x4C,
//     0x70,
//     0x03, //这里要变为0x7D,0x03
// };


//尾部 
//帧检验序列FCS  F
byte udp[1500];
byte ip[1500];
byte frame[1508];   //帧

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


unsigned short CRC16(byte* data,unsigned short datalen)
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
// udp报文生成
unsigned short generateUDP(byte* from_port, byte* to_port,byte* udplen,
byte* check_sum,byte* data_app_to_trans,unsigned short datalen,byte* udp){
    memcpy(&udp[0],from_port,2);
    memcpy(&udp[2],to_port,2);
    memcpy(&udp[4],udplen,2);
    memcpy(&udp[6],check_sum,2);
    memcpy(&udp[8],data_app_to_trans,datalen);
    return datalen+8;
}

// 数据报生成
unsigned short generateIP(byte* version_head, byte* diffserv, byte*sum_length, byte* identification,
byte*flag_divide, byte*TTL, byte* protocol, byte* head_test, byte*from_ip, byte*to_ip, 
unsigned short datalen,byte* data_trans_to_ip,byte* ip ){
    memcpy(&ip[0],version_head,1);
    memcpy(&ip[1],diffserv,1);
    memcpy(&ip[2],sum_length,2);
    memcpy(&ip[4],identification,2);
    memcpy(&ip[6],flag_divide,2);
    memcpy(&ip[8],TTL,1);
    memcpy(&ip[9],protocol,1);
    memcpy(&ip[10],head_test,2);
    memcpy(&ip[12],from_ip,4);
    memcpy(&ip[16],to_ip,4);
    memcpy(&ip[20],data_trans_to_ip,datalen);
    return datalen+20; //返回数据报长度
}
// 帧生成
unsigned short generateFrame(byte *F, byte *A, byte *C,byte *type,byte *data,unsigned short datalen, byte *frame) //生成帧
{
    //memcpy函数有三个参数，第一个是目标地址，第二个是源地址，第三个是数据长度(单位是字节)
    memcpy(&frame[0], F, 1);                 //F
    memcpy(&frame[1], A, 1);                 //A
    memcpy(&frame[2], C, 1);                 //C
    memcpy(&frame[3], type, 2);              //Protocol Type放入帧
    memcpy(&frame[5], data, datalen);      //数据部分放入帧
    int tail = datalen + 5;                //此时数据部分的末端(也是此时帧的末端,帧校验序列之前)
    unsigned short FCS;                     //帧校验序列
    FCS = CRC16(frame, tail);               //生成帧校验序列
    memcpy(&frame[tail], &FCS, 2);          //帧校验序列放入帧
    memcpy(&frame[tail+2], F, 1);           //F
    return datalen + 8;                //帧的实际长度
}


void sendFrame(byte *frame, unsigned short len, FILE *fp) //发送帧
{
    //fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
    fwrite(&len, sizeof(len), 1, fp);     //写入帧的总长度 在第一个字节
    fwrite(frame, sizeof(byte), len, fp); //写入帧
    printf("send succeed.\n");
}

// int 转换为 byte
void IntToByte(int value, unsigned char* bytes)
{
    size_t length = sizeof(int);
    memset(bytes, 0, sizeof(unsigned char) * length);
    bytes[0] = (unsigned char)(0xff & value);
    bytes[1] = (unsigned char)((0xff00 & value) >> 8);
    bytes[2] = (unsigned char)((0xff0000 & value) >> 16);
    bytes[3] = (unsigned char)((0xff000000 & value) >> 24);
}

// byte 转换为 int
int ByteToInt(unsigned char* byteArray)
{
    int value = byteArray[0] & 0xFF;
    value |= ((byteArray[1] << 8) & 0xFF00);
    value |= ((byteArray[2] << 16) & 0xFF0000);
    value |= ((byteArray[3] << 24) & 0xFF000000);
    return value;
}

//ip数据报首部检验和确定
void confirm_head_test(byte* version_head,byte* diffserv,byte* sum_length,
byte* identification, byte* flag_divide, byte* TTL, byte* protocol,
byte* head_test, byte* from_ip, byte* to_ip){
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
    head_test[0] = tp >> 8;
    head_test[1] = tp & 0xff; 
}

//udp报文检验和确定
void confirm_check_sum(byte* udp_from_ip,byte* udp_to_ip, byte* zero, 
byte* udp_17, byte* false_udplen, byte* from_port, byte* to_port,
byte* udplen, byte* check_sum, byte* data_app_to_trans,unsigned short app_data_len){
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
    int length = app_data_len;  //可能要改
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
    check_sum[0] = tp >> 8;
    check_sum[1] = tp & 0xff;
}

int main()
{
    byte data[1500];
    printf("请输入你要传输的数据: \n");
    scanf("%[^\n]",data);

    //从文件中读取IP报文段
    FILE *fp = fopen("mac.frm", "w");
    // ---------------------------运输层实现----------------------------
    unsigned short app_data_len=strlen(data);
    byte data_app_to_trans[1500];
    memcpy(data_app_to_trans,data,sizeof(data));
    //确定udp数据报长度
    uint32_t udp_temp;
    int temp_res_udp=8+strlen(data_app_to_trans);
    byte temp_res_udp_b[4];
    IntToByte(temp_res_udp,temp_res_udp_b);
    udp_temp=(temp_res_udp_b[1] << 8) | temp_res_udp_b[0];
    udplen[0] = udp_temp >> 8;
    udplen[1] = udp_temp & 0xff;
    false_udplen[0] = udp_temp >> 8;
    false_udplen[1] = udp_temp & 0xff;
    //计算检验和
    confirm_check_sum(udp_from_ip,udp_to_ip,zero,udp_17,false_udplen,from_port,to_port,udplen,check_sum,data_app_to_trans,app_data_len);
    //封装报文
    unsigned short udp_data_len=generateUDP(from_port,to_port,udplen,check_sum,data_app_to_trans,strlen(data_app_to_trans),udp);
    printf("udp: %d\n",udp_data_len);
    // ---------------------------网络层实现----------------------------
    byte data_trans_to_ip[udp_data_len];
    memcpy(data_trans_to_ip,udp,udp_data_len);
    // 确定首部+数据部分的总长度
    uint32_t temp;
    int temp_res_ip=20+udp_data_len;
    byte temp_res_ip_b[4];
    IntToByte(temp_res_ip,temp_res_ip_b);
    temp=(temp_res_ip_b[1] << 8) | temp_res_ip_b[0];
    sum_length[0]=temp >> 8;
    sum_length[1]=temp & 0xff;
    // 计算检验和
    confirm_head_test(version_head,diffserv,sum_length,identification,flag_divide,TTL,protocol,head_test,from_ip,to_ip);
    // 封装数据报
    unsigned short ip_data_len=generateIP(version_head,diffserv,sum_length,identification,flag_divide,TTL,protocol,head_test,from_ip,to_ip,udp_data_len,data_trans_to_ip,ip);
    printf("ip: %d \n",ip_data_len);


    // ---------------------------数据链路层实现------------------------
    //PPP不考虑信息部分最小情况
    byte data_ip_to_mac[ip_data_len];
    memcpy(data_ip_to_mac,ip,ip_data_len);
    unsigned short datalen = sizeof(data_ip_to_mac);
    //检查信息部分长度
    if (datalen > 1500)
    {
        printf("帧的信息字段 %u 超过1500字节.\n", datalen);
        printf("send error\n");
        return 0;
    }
    unsigned short frameLen; //帧的实际长度

    int num=0;
    //字节填充
    for(int i=0;i<datalen;i++)
    {
        if(data_ip_to_mac[i]==0x7E || data_ip_to_mac[i]==0x7D || data_ip_to_mac[i]<0x20)
        {
            num++;
        }
    }
    byte good_data[datalen+num];
    int j=0;
    for(int i=0;i<datalen;i++)
    {
        if(data_ip_to_mac[i]==0x7E)
        {
            good_data[j]=0x7D;
            good_data[j+1]=0x5E;
            j+=2;
        }
        else if(data_ip_to_mac[i]==0x7D)
        {
            good_data[j]=0x7D;
            good_data[j+1]=0x5D;
            j+=2;
        }
        else if(data_ip_to_mac[i]<0x20)
        {
            good_data[j]=0x7D;
            good_data[j+1]=data_ip_to_mac[i];
            j+=2;
        }
        else
        {
            good_data[j]=data_ip_to_mac[i];
            j+=1;
        }
    }
    unsigned short gooddatalen = sizeof(good_data);

    // printf("\n");
    // for(int i=0;i<datalen;i++)
    // {
    //     printf("%02x",data[i]);
    // }
    // printf("\n");

    // printf("\n");
    // for(int i=0;i<gooddatalen;i++)
    // {
    //     printf("%02x",good_data[i]);
    // }
    // printf("\n");

    //完整且正确
    frameLen = generateFrame(F, A , C, type , good_data, gooddatalen , frame);
    sendFrame(frame, frameLen, fp);
    
    // printf("\n");
    // for(int i=0;i<frameLen;i++)
    // {
    //     printf("%02x",frame[i]);
    // }


    //某一位出错
    frameLen = generateFrame(F, A , C, type ,  good_data, gooddatalen , frame);
    int error_pos = rand() % frameLen;
    frame[error_pos] ^= 1;
    sendFrame(frame, frameLen, fp);


    fclose(fp);
    return 0;
}