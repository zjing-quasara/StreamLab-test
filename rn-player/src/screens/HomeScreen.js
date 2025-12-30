import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { initConfig } from '../utils/api';
import { checkForUpdate, markUpdateSuccess } from '../utils/update';

const hotMovies = [
  { name: '长安十二时辰', tag: '48集' },
  { name: '长安二十四计', tag: '28集' },
  { name: '狂飙', tag: '热门' },
  { name: '繁花', tag: '热门' },
  { name: '庆余年', tag: '热门' },
  { name: '三体', tag: '科幻' },
];

export default function HomeScreen({ navigation }) {
  const [keyword, setKeyword] = useState('');

  useEffect(() => {
    // 初始化
    initConfig();
    // 标记更新成功
    markUpdateSuccess();
    // 静默检查更新
    checkForUpdate(true);
  }, []);

  const doSearch = () => {
    if (!keyword.trim()) {
      return;
    }
    navigation.navigate('Search', { keyword });
  };

  const quickSearch = (name) => {
    setKeyword(name);
    navigation.navigate('Search', { keyword: name });
  };

  return (
    <ScrollView style={styles.container}>
      {/* 搜索框 */}
      <View style={styles.searchBox}>
        <TextInput
          style={styles.input}
          placeholder="输入影视名称搜索"
          placeholderTextColor="#666"
          value={keyword}
          onChangeText={setKeyword}
          onSubmitEditing={doSearch}
        />
        <TouchableOpacity style={styles.searchBtn} onPress={doSearch}>
          <Text style={styles.searchBtnText}>搜索</Text>
        </TouchableOpacity>
      </View>

      {/* 热门推荐 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>热门推荐</Text>
        <View style={styles.movieGrid}>
          {hotMovies.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.movieItem}
              onPress={() => quickSearch(item.name)}
            >
              <Text style={styles.movieName}>{item.name}</Text>
              <Text style={styles.movieTag}>{item.tag}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* 说明 */}
      <View style={styles.tips}>
        <Text style={styles.tipText}>StreamLab - 流媒体技术研究</Text>
        <Text style={styles.tipText}>资源来自第三方，仅供学习研究</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    padding: 15,
  },
  searchBox: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 20,
  },
  input: {
    flex: 1,
    height: 45,
    backgroundColor: '#1a1a2e',
    borderRadius: 25,
    paddingHorizontal: 20,
    color: '#fff',
    fontSize: 15,
  },
  searchBtn: {
    width: 70,
    height: 45,
    backgroundColor: '#00d4ff',
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchBtnText: {
    color: '#000',
    fontSize: 15,
    fontWeight: 'bold',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    color: '#888',
    fontSize: 14,
    marginBottom: 12,
  },
  movieGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  movieItem: {
    backgroundColor: '#1a1a2e',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  movieName: {
    color: '#fff',
    fontSize: 14,
  },
  movieTag: {
    color: '#00d4ff',
    fontSize: 11,
    marginTop: 3,
  },
  tips: {
    marginTop: 40,
    alignItems: 'center',
  },
  tipText: {
    color: '#444',
    fontSize: 12,
    marginBottom: 5,
  },
});

