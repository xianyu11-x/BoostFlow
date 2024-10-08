
def read_txt(intput_path,output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        with open(intput_path, 'r', encoding='utf-8') as infile:
            data2 = []
            for line in infile:
                data_line = line.strip("\n").split()  # 去除首尾换行符，并按空格划分
                print(data_line)
                data2.append(data_line)
            print(data2)
            for line in data2:
                # data = '' + '\t'.join(str(i) for i in line) + '\n'  # 用\t隔开
                data = '' + ' '.join(str(i) for i in line) + '\n'  # 用空格隔开
                file.write(data)

if __name__=="__main__":
    intput_path="./dump3.txt"
    output_path="./split3.txt"
    read_txt(intput_path,output_path)