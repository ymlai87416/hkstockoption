package com.ymlai87416.stockoption.server.domain;

import javax.persistence.*;

/**
 * Created by Tom on 18/10/2016.
 */
@Entity
@Table(name = "key_value_collection")
public class KeyValuePair {
    private Long id;
    private String key;
    private String value;
    private long version;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }
    @Column(name = "`key`")
    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    @Column(name = "`value`")
    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    @Version
    @Column(name = "version")
    public long getVersion() {
        return version;
    }

    public void setVersion(long version) {
        this.version = version;
    }
}
